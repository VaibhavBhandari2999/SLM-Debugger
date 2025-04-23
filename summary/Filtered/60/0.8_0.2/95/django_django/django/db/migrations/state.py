import copy
from collections import defaultdict
from contextlib import contextmanager
from functools import partial

from django.apps import AppConfig
from django.apps.registry import Apps
from django.apps.registry import apps as global_apps
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.migrations.utils import field_is_referenced, get_references
from django.db.models import NOT_PROVIDED
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT
from django.db.models.options import DEFAULT_NAMES, normalize_together
from django.db.models.utils import make_model_tuple
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.version import get_docs_version

from .exceptions import InvalidBasesError
from .utils import resolve_relation


def _get_app_label_and_model_name(model, app_label=""):
    if isinstance(model, str):
        split = model.split(".", 1)
        return tuple(split) if len(split) == 2 else (app_label, split[0])
    else:
        return model._meta.app_label, model._meta.model_name


def _get_related_models(m):
    """Return all models that have a direct relationship to the given model."""
    related_models = [
        subclass
        for subclass in m.__subclasses__()
        if issubclass(subclass, models.Model)
    ]
    related_fields_models = set()
    for f in m._meta.get_fields(include_parents=True, include_hidden=True):
        if (
            f.is_relation
            and f.related_model is not None
            and not isinstance(f.related_model, str)
        ):
            related_fields_models.add(f.model)
            related_models.append(f.related_model)
    # Reverse accessors of foreign keys to proxy models are attached to their
    # concrete proxied model.
    opts = m._meta
    if opts.proxy and m in related_fields_models:
        related_models.append(opts.concrete_model)
    return related_models


def get_related_models_tuples(model):
    """
    Return a list of typical (app_label, model_name) tuples for all related
    models for the given model.
    """
    return {
        (rel_mod._meta.app_label, rel_mod._meta.model_name)
        for rel_mod in _get_related_models(model)
    }


def get_related_models_recursive(model):
    """
    Return all models that have a direct or indirect relationship
    to the given model.

    Relationships are either defined by explicit relational fields, like
    ForeignKey, ManyToManyField or OneToOneField, or by inheriting from another
    model (a superclass is related to its subclasses, but not vice versa). Note,
    however, that a model inheriting from a concrete model is also related to
    its superclass through the implicit *_ptr OneToOneField on the subclass.
    """
    seen = set()
    queue = _get_related_models(model)
    for rel_mod in queue:
        rel_app_label, rel_model_name = (
            rel_mod._meta.app_label,
            rel_mod._meta.model_name,
        )
        if (rel_app_label, rel_model_name) in seen:
            continue
        seen.add((rel_app_label, rel_model_name))
        queue.extend(_get_related_models(rel_mod))
    return seen - {(model._meta.app_label, model._meta.model_name)}


class ProjectState:
    """
    Represent the entire project's overall state. This is the item that is
    passed around - do it here rather than at the app level so that cross-app
    FKs/etc. resolve properly.
    """

    def __init__(self, models=None, real_apps=None):
        """
        Initialize the object with models and real_apps.
        
        Args:
        models (dict, optional): A dictionary of models. Defaults to an empty dictionary.
        real_apps (set, optional): A set of real applications. Defaults to an empty set.
        
        Attributes:
        models (dict): A dictionary of models.
        real_apps (set): A set of real applications.
        is_delayed (bool): Indicates if the initialization is delayed.
        _relations (dict): A dictionary containing remote model keys,
        """

        self.models = models or {}
        # Apps to include from main registry, usually unmigrated ones
        if real_apps is None:
            real_apps = set()
        else:
            assert isinstance(real_apps, set)
        self.real_apps = real_apps
        self.is_delayed = False
        # {remote_model_key: {model_key: {field_name: field}}}
        self._relations = None

    @property
    def relations(self):
        if self._relations is None:
            self.resolve_fields_and_relations()
        return self._relations

    def add_model(self, model_state):
        """
        Add a model to the internal state.
        
        This function adds a model state to the internal state dictionary and optionally resolves model relations and reloads the model.
        
        Parameters:
        model_state (ModelState): The model state to be added.
        
        Returns:
        None: This function does not return any value.
        
        Keywords:
        model_state: The model state to be added.
        model_key: A tuple containing the app label and the lowercased model name.
        models: The internal dictionary where the model state is stored
        """

        model_key = model_state.app_label, model_state.name_lower
        self.models[model_key] = model_state
        if self._relations is not None:
            self.resolve_model_relations(model_key)
        if "apps" in self.__dict__:  # hasattr would cache the property
            self.reload_model(*model_key)

    def remove_model(self, app_label, model_name):
        model_key = app_label, model_name
        del self.models[model_key]
        if self._relations is not None:
            self._relations.pop(model_key, None)
            # Call list() since _relations can change size during iteration.
            for related_model_key, model_relations in list(self._relations.items()):
                model_relations.pop(model_key, None)
                if not model_relations:
                    del self._relations[related_model_key]
        if "apps" in self.__dict__:  # hasattr would cache the property
            self.apps.unregister_model(*model_key)
            # Need to do this explicitly since unregister_model() doesn't clear
            # the cache automatically (#24513)
            self.apps.clear_cache()

    def rename_model(self, app_label, old_name, new_name):
        # Add a new model.
        old_name_lower = old_name.lower()
        new_name_lower = new_name.lower()
        renamed_model = self.models[app_label, old_name_lower].clone()
        renamed_model.name = new_name
        self.models[app_label, new_name_lower] = renamed_model
        # Repoint all fields pointing to the old model to the new one.
        old_model_tuple = (app_label, old_name_lower)
        new_remote_model = f"{app_label}.{new_name}"
        to_reload = set()
        for model_state, name, field, reference in get_references(
            self, old_model_tuple
        ):
            changed_field = None
            if reference.to:
                changed_field = field.clone()
                changed_field.remote_field.model = new_remote_model
            if reference.through:
                if changed_field is None:
                    changed_field = field.clone()
                changed_field.remote_field.through = new_remote_model
            if changed_field:
                model_state.fields[name] = changed_field
                to_reload.add((model_state.app_label, model_state.name_lower))
        if self._relations is not None:
            old_name_key = app_label, old_name_lower
            new_name_key = app_label, new_name_lower
            if old_name_key in self._relations:
                self._relations[new_name_key] = self._relations.pop(old_name_key)
            for model_relations in self._relations.values():
                if old_name_key in model_relations:
                    model_relations[new_name_key] = model_relations.pop(old_name_key)
        # Reload models related to old model before removing the old model.
        self.reload_models(to_reload, delay=True)
        # Remove the old model.
        self.remove_model(app_label, old_name_lower)
        self.reload_model(app_label, new_name_lower, delay=True)

    def alter_model_options(self, app_label, model_name, options, option_keys=None):
        model_state = self.models[app_label, model_name]
        model_state.options = {**model_state.options, **options}
        if option_keys:
            for key in option_keys:
                if key not in options:
                    model_state.options.pop(key, False)
        self.reload_model(app_label, model_name, delay=True)

    def remove_model_options(self, app_label, model_name, option_name, value_to_remove):
        model_state = self.models[app_label, model_name]
        if objs := model_state.options.get(option_name):
            model_state.options[option_name] = [
                obj for obj in objs if tuple(obj) != tuple(value_to_remove)
            ]
        self.reload_model(app_label, model_name, delay=True)

    def alter_model_managers(self, app_label, model_name, managers):
        model_state = self.models[app_label, model_name]
        model_state.managers = list(managers)
        self.reload_model(app_label, model_name, delay=True)

    def _append_option(self, app_label, model_name, option_name, obj):
        model_state = self.models[app_label, model_name]
        model_state.options[option_name] = [*model_state.options[option_name], obj]
        self.reload_model(app_label, model_name, delay=True)

    def _remove_option(self, app_label, model_name, option_name, obj_name):
        model_state = self.models[app_label, model_name]
        objs = model_state.options[option_name]
        model_state.options[option_name] = [obj for obj in objs if obj.name != obj_name]
        self.reload_model(app_label, model_name, delay=True)

    def add_index(self, app_label, model_name, index):
        self._append_option(app_label, model_name, "indexes", index)

    def remove_index(self, app_label, model_name, index_name):
        self._remove_option(app_label, model_name, "indexes", index_name)

    def rename_index(self, app_label, model_name, old_index_name, new_index_name):
        """
        Renames an index in the Django model options.
        
        This function updates the index name in the model options for a specific Django app and model.
        
        Parameters:
        app_label (str): The label of the Django app containing the model.
        model_name (str): The name of the Django model.
        old_index_name (str): The current name of the index to be renamed.
        new_index_name (str): The new name for the index.
        
        Returns:
        None: This function does not return
        """

        model_state = self.models[app_label, model_name]
        objs = model_state.options["indexes"]

        new_indexes = []
        for obj in objs:
            if obj.name == old_index_name:
                obj = obj.clone()
                obj.name = new_index_name
            new_indexes.append(obj)

        model_state.options["indexes"] = new_indexes
        self.reload_model(app_label, model_name, delay=True)

    def add_constraint(self, app_label, model_name, constraint):
        self._append_option(app_label, model_name, "constraints", constraint)

    def remove_constraint(self, app_label, model_name, constraint_name):
        self._remove_option(app_label, model_name, "constraints", constraint_name)

    def add_field(self, app_label, model_name, name, field, preserve_default):
        # If preserve default is off, don't use the default for future state.
        if not preserve_default:
            field = field.clone()
            field.default = NOT_PROVIDED
        else:
            field = field
        model_key = app_label, model_name
        self.models[model_key].fields[name] = field
        if self._relations is not None:
            self.resolve_model_field_relations(model_key, name, field)
        # Delay rendering of relationships if it's not a relational field.
        delay = not field.is_relation
        self.reload_model(*model_key, delay=delay)

    def remove_field(self, app_label, model_name, name):
        model_key = app_label, model_name
        model_state = self.models[model_key]
        old_field = model_state.fields.pop(name)
        if self._relations is not None:
            self.resolve_model_field_relations(model_key, name, old_field)
        # Delay rendering of relationships if it's not a relational field.
        delay = not old_field.is_relation
        self.reload_m
