"""
This Python file contains a suite of functions and a class designed to handle the deletion of related objects in a Django application. The core functionality revolves around managing deletions in a way that respects various constraints and ensures data integrity.

#### Classes:
- **Collector**: Manages the collection and deletion of related objects. It handles the addition of objects to be deleted, tracks dependencies, and sorts models based on their dependencies to ensure proper deletion order.

#### Functions:
- **CASCADE, PROTECT, RESTRICT, SET, SET_NULL, SET_DEFAULT, DO_NOTHING**: These functions define different behaviors for handling deletions, such as cascading deletions, protecting related objects, setting default values, etc.
- **get_candidate_relations_to_delete**: Filters fields that
"""
from collections import Counter, defaultdict
from functools import partial
from itertools import chain
from operator import attrgetter

from django.db import IntegrityError, connections, transaction
from django.db.models import query_utils, signals, sql


class ProtectedError(IntegrityError):
    def __init__(self, msg, protected_objects):
        self.protected_objects = protected_objects
        super().__init__(msg, protected_objects)


class RestrictedError(IntegrityError):
    def __init__(self, msg, restricted_objects):
        self.restricted_objects = restricted_objects
        super().__init__(msg, restricted_objects)


def CASCADE(collector, field, sub_objs, using):
    """
    Collects related objects for a given field and its sub-objects, handling null values and constraint checks.
    
    Args:
    collector (BaseCollector): The collector object used to collect related objects.
    field (Field): The field object representing the relationship between models.
    sub_objs (QuerySet): A queryset of sub-objects to be collected.
    using (str): The database alias indicating which database to use.
    
    Summary:
    This function is responsible for collecting related objects for a given field
    """

    collector.collect(
        sub_objs,
        source=field.remote_field.model,
        source_attr=field.name,
        nullable=field.null,
        fail_on_restricted=False,
    )
    if field.null and not connections[using].features.can_defer_constraint_checks:
        collector.add_field_update(field, None, sub_objs)


def PROTECT(collector, field, sub_objs, using):
    """
    Raises a ProtectedError when attempting to delete related instances of a model through a protected foreign key.
    
    Args:
    collector (BaseModelDeletionCollector): The deletion collector instance.
    field (Field): The field representing the protected foreign key.
    sub_objs (list): A list of related objects that would be affected by the deletion.
    using (str): The database alias to use for the operation.
    
    Raises:
    ProtectedError: If any of the related objects cannot be deleted due to
    """

    raise ProtectedError(
        "Cannot delete some instances of model '%s' because they are "
        "referenced through a protected foreign key: '%s.%s'"
        % (
            field.remote_field.model.__name__,
            sub_objs[0].__class__.__name__,
            field.name,
        ),
        sub_objs,
    )


def RESTRICT(collector, field, sub_objs, using):
    collector.add_restricted_objects(field, sub_objs)
    collector.add_dependency(field.remote_field.model, field.model)


def SET(value):
    """
    Sets the value of a model field on delete.
    
    Args:
    value (callable or object): The value to set on delete. If callable, it will be called with no arguments and its result will be used as the value.
    
    Returns:
    set_on_delete (function): A function that updates the field value on delete.
    
    Example:
    >>> SET(lambda: 'deleted')
    <function set_on_delete at 0x7f9c3c3c3c3c
    """

    if callable(value):

        def set_on_delete(collector, field, sub_objs, using):
            collector.add_field_update(field, value(), sub_objs)

    else:

        def set_on_delete(collector, field, sub_objs, using):
            collector.add_field_update(field, value, sub_objs)

    set_on_delete.deconstruct = lambda: ("django.db.models.SET", (value,), {})
    return set_on_delete


def SET_NULL(collector, field, sub_objs, using):
    collector.add_field_update(field, None, sub_objs)


def SET_DEFAULT(collector, field, sub_objs, using):
    collector.add_field_update(field, field.get_default(), sub_objs)


def DO_NOTHING(collector, field, sub_objs, using):
    pass


def get_candidate_relations_to_delete(opts):
    """
    Retrieve candidate relations for deletion.
    
    Args:
    opts (ModelOptions): The model options object containing information about the fields of the model.
    
    Yields:
    Field: Fields that are candidates for deletion, specifically those that are auto-created, non-concrete, and either one-to-one or one-to-many relations.
    
    This function filters through the fields of a given model options object to identify candidate relations for deletion. It focuses on fields that are auto-created, non-concrete, and either one
    """

    # The candidate relations are the ones that come from N-1 and 1-1 relations.
    # N-N  (i.e., many-to-many) relations aren't candidates for deletion.
    return (
        f
        for f in opts.get_fields(include_hidden=True)
        if f.auto_created and not f.concrete and (f.one_to_one or f.one_to_many)
    )


class Collector:
    def __init__(self, using, origin=None):
        """
        Initializes an instance of the class with the given `using` database alias and optional `origin` model or QuerySet.
        
        Args:
        using (str): The database alias to use for operations.
        origin (Model or QuerySet, optional): The source model or QuerySet from which data will be processed.
        
        Attributes:
        using (str): The database alias to use for operations.
        origin (Model or QuerySet, optional): The source model or QuerySet from which data will
        """

        self.using = using
        # A Model or QuerySet object.
        self.origin = origin
        # Initially, {model: {instances}}, later values become lists.
        self.data = defaultdict(set)
        # {model: {(field, value): {instances}}}
        self.field_updates = defaultdict(partial(defaultdict, set))
        # {model: {field: {instances}}}
        self.restricted_objects = defaultdict(partial(defaultdict, set))
        # fast_deletes is a list of queryset-likes that can be deleted without
        # fetching the objects into memory.
        self.fast_deletes = []

        # Tracks deletion-order dependency for databases without transactions
        # or ability to defer constraint checks. Only concrete model classes
        # should be included, as the dependencies exist only between actual
        # database tables; proxy models are represented here by their concrete
        # parent.
        self.dependencies = defaultdict(set)  # {model: {models}}

    def add(self, objs, source=None, nullable=False, reverse_dependency=False):
        """
        Add 'objs' to the collection of objects to be deleted.  If the call is
        the result of a cascade, 'source' should be the model that caused it,
        and 'nullable' should be set to True if the relation can be null.

        Return a list of all objects that were not already collected.
        """
        if not objs:
            return []
        new_objs = []
        model = objs[0].__class__
        instances = self.data[model]
        for obj in objs:
            if obj not in instances:
                new_objs.append(obj)
        instances.update(new_objs)
        # Nullable relationships can be ignored -- they are nulled out before
        # deleting, and therefore do not affect the order in which objects have
        # to be deleted.
        if source is not None and not nullable:
            self.add_dependency(source, model, reverse_dependency=reverse_dependency)
        return new_objs

    def add_dependency(self, model, dependency, reverse_dependency=False):
        """
        Adds a dependency relationship between two models.
        
        Args:
        model (Model): The primary model that depends on another model.
        dependency (Model): The model that is depended upon by the primary model.
        reverse_dependency (bool, optional): Indicates whether the dependency should be reversed. Defaults to False.
        
        This method updates the dependencies dictionary to reflect the relationship between the two models. If `reverse_dependency` is True, the roles of `model` and `dependency` are swapped before adding the
        """

        if reverse_dependency:
            model, dependency = dependency, model
        self.dependencies[model._meta.concrete_model].add(
            dependency._meta.concrete_model
        )
        self.data.setdefault(dependency, self.data.default_factory())

    def add_field_update(self, field, value, objs):
        """
        Schedule a field update. 'objs' must be a homogeneous iterable
        collection of model instances (e.g. a QuerySet).
        """
        if not objs:
            return
        model = objs[0].__class__
        self.field_updates[model][field, value].update(objs)

    def add_restricted_objects(self, field, objs):
        """
        Adds restricted objects to the specified field.
        
        Args:
        field (str): The field to which the objects are being added.
        objs (list): A list of objects to be added.
        
        Effects:
        Updates the `restricted_objects` dictionary with the provided objects for the given field and model class.
        """

        if objs:
            model = objs[0].__class__
            self.restricted_objects[model][field].update(objs)

    def clear_restricted_objects_from_set(self, model, objs):
        """
        Clears restricted objects from a set based on the given model.
        
        Args:
        model (str): The model name whose restricted objects need to be cleared.
        objs (set): A set of objects to be removed from the restricted objects.
        
        Returns:
        None: This function modifies the `self.restricted_objects` dictionary in place.
        
        Notes:
        - The function checks if the given `model` exists in `self.restricted_objects`.
        - If the `model` is found
        """

        if model in self.restricted_objects:
            self.restricted_objects[model] = {
                field: items - objs
                for field, items in self.restricted_objects[model].items()
            }

    def clear_restricted_objects_from_queryset(self, model, qs):
        """
        Clears restricted objects from a queryset based on the specified model.
        
        Args:
        model (Model): The Django model class for which to clear restricted objects.
        qs (QuerySet): The queryset from which to remove restricted objects.
        
        This function filters the queryset to identify restricted objects based on the `restricted_objects` dictionary, then clears those objects from the given queryset using the `clear_restricted_objects_from_set` method.
        """

        if model in self.restricted_objects:
            objs = set(
                qs.filter(
                    pk__in=[
                        obj.pk
                        for objs in self.restricted_objects[model].values()
                        for obj in objs
                    ]
                )
            )
            self.clear_restricted_objects_from_set(model, objs)

    def _has_signal_listeners(self, model):
        """
        Determines if the given model has any signal listeners for pre-delete or post-delete operations.
        
        Args:
        model (Model): The Django model instance to check for signal listeners.
        
        Returns:
        bool: True if the model has any pre-delete or post-delete signal listeners, False otherwise.
        """

        return signals.pre_delete.has_listeners(
            model
        ) or signals.post_delete.has_listeners(model)

    def can_fast_delete(self, objs, from_field=None):
        """
        Determine if the objects in the given queryset-like or single object
        can be fast-deleted. This can be done if there are no cascades, no
        parents and no signal listeners for the object class.

        The 'from_field' tells where we are coming from - we need this to
        determine if the objects are in fact to be deleted. Allow also
        skipping parent -> child -> parent chain preventing fast delete of
        the child.
        """
        if from_field and from_field.remote_field.on_delete is not CASCADE:
            return False
        if hasattr(objs, "_meta"):
            model = objs._meta.model
        elif hasattr(objs, "model") and hasattr(objs, "_raw_delete"):
            model = objs.model
        else:
            return False
        if self._has_signal_listeners(model):
            return False
        # The use of from_field comes from the need to avoid cascade back to
        # parent when parent delete is cascading to child.
        opts = model._meta
        return (
            all(
                link == from_field
                for link in opts.concrete_model._meta.parents.values()
            )
            and
            # Foreign keys pointing to this model.
            all(
                related.field.remote_field.on_delete is DO_NOTHING
                for related in get_candidate_relations_to_delete(opts)
            )
            and (
                # Something like generic foreign key.
                not any(
                    hasattr(field, "bulk_related_objects")
                    for field in opts.private_fields
                )
            )
        )

    def get_del_batches(self, objs, fields):
        """
        Return the objs in suitably sized batches for the used connection.
        """
        field_names = [field.name for field in fields]
        conn_batch_size = max(
            connections[self.using].ops.bulk_batch_size(field_names, objs), 1
        )
        if len(objs) > conn_batch_size:
            return [
                objs[i : i + conn_batch_size]
                for i in range(0, len(objs), conn_batch_size)
            ]
        else:
            return [objs]

    def collect(
        self,
        objs,
        source=None,
        nullable=False,
        collect_related=True,
        source_attr=None,
        reverse_dependency=False,
        keep_parents=False,
        fail_on_restricted=True,
    ):
        """
        Add 'objs' to the collection of objects to be deleted as well as all
        parent instances.  'objs' must be a homogeneous iterable collection of
        model instances (e.g. a QuerySet).  If 'collect_related' is True,
        related objects will be handled by their respective on_delete handler.

        If the call is the result of a cascade, 'source' should be the model
        that caused it and 'nullable' should be set to True, if the relation
        can be null.

        If 'reverse_dependency' is True, 'source' will be deleted before the
        current model, rather than after. (Needed for cascading to parent
        models, the one case in which the cascade follows the forwards
        direction of an FK rather than the reverse direction.)

        If 'keep_parents' is True, data of parent model's will be not deleted.

        If 'fail_on_restricted' is False, error won't be raised even if it's
        prohibited to delete such objects due to RESTRICT, that defers
        restricted object checking in recursive calls where the top-level call
        may need to collect more objects to determine whether restricted ones
        can be deleted.
        """
        if self.can_fast_delete(objs):
            self.fast_deletes.append(objs)
            return
        new_objs = self.add(
            objs, source, nullable, reverse_dependency=reverse_dependency
        )
        if not new_objs:
            return

        model = new_objs[0].__class__

        if not keep_parents:
            # Recursively collect concrete model's parent models, but not their
            # related objects. These will be found by meta.get_fields()
            concrete_model = model._meta.concrete_model
            for ptr in concrete_model._meta.parents.values():
                if ptr:
                    parent_objs = [getattr(obj, ptr.name) for obj in new_objs]
                    self.collect(
                        parent_objs,
                        source=model,
                        source_attr=ptr.remote_field.related_name,
                        collect_related=False,
                        reverse_dependency=True,
                        fail_on_restricted=False,
                    )
        if not collect_related:
            return

        if keep_parents:
            parents = set(model._meta.get_parent_list())
        model_fast_deletes = defaultdict(list)
        protected_objects = defaultdict(list)
        for related in get_candidate_relations_to_delete(model._meta):
            # Preserve parent reverse relationships if keep_parents=True.
            if keep_parents and related.model in parents:
                continue
            field = related.field
            if field.remote_field.on_delete == DO_NOTHING:
                continue
            related_model = related.related_model
            if self.can_fast_delete(related_model, from_field=field):
                model_fast_deletes[related_model].append(field)
                continue
            batches = self.get_del_batches(new_objs, [field])
            for batch in batches:
                sub_objs = self.related_objects(related_model, [field], batch)
                # Non-referenced fields can be deferred if no signal receivers
                # are connected for the related model as they'll never be
                # exposed to the user. Skip field deferring when some
                # relationships are select_related as interactions between both
                # features are hard to get right. This should only happen in
                # the rare cases where .related_objects is overridden anyway.
                if not (
                    sub_objs.query.select_related
                    or self._has_signal_listeners(related_model)
                ):
                    referenced_fields = set(
                        chain.from_iterable(
                            (rf.attname for rf in rel.field.foreign_related_fields)
                            for rel in get_candidate_relations_to_delete(
                                related_model._meta
                            )
                        )
                    )
                    sub_objs = sub_objs.only(*tuple(referenced_fields))
                if sub_objs:
                    try:
                        field.remote_field.on_delete(self, field, sub_objs, self.using)
                    except ProtectedError as error:
                        key = "'%s.%s'" % (field.model.__name__, field.name)
                        protected_objects[key] += error.protected_objects
        if protected_objects:
            raise ProtectedError(
                "Cannot delete some instances of model %r because they are "
                "referenced through protected foreign keys: %s."
                % (
                    model.__name__,
                    ", ".join(protected_objects),
                ),
                set(chain.from_iterable(protected_objects.values())),
            )
        for related_model, related_fields in model_fast_deletes.items():
            batches = self.get_del_batches(new_objs, related_fields)
            for batch in batches:
                sub_objs = self.related_objects(related_model, related_fields, batch)
                self.fast_deletes.append(sub_objs)
        for field in model._meta.private_fields:
            if hasattr(field, "bulk_related_objects"):
                # It's something like generic foreign key.
                sub_objs = field.bulk_related_objects(new_objs, self.using)
                self.collect(
                    sub_objs, source=model, nullable=True, fail_on_restricted=False
                )

        if fail_on_restricted:
            # Raise an error if collected restricted objects (RESTRICT) aren't
            # candidates for deletion also collected via CASCADE.
            for related_model, instances in self.data.items():
                self.clear_restricted_objects_from_set(related_model, instances)
            for qs in self.fast_deletes:
                self.clear_restricted_objects_from_queryset(qs.model, qs)
            if self.restricted_objects.values():
                restricted_objects = defaultdict(list)
                for related_model, fields in self.restricted_objects.items():
                    for field, objs in fields.items():
                        if objs:
                            key = "'%s.%s'" % (related_model.__name__, field.name)
                            restricted_objects[key] += objs
                if restricted_objects:
                    raise RestrictedError(
                        "Cannot delete some instances of model %r because "
                        "they are referenced through restricted foreign keys: "
                        "%s."
                        % (
                            model.__name__,
                            ", ".join(restricted_objects),
                        ),
                        set(chain.from_iterable(restricted_objects.values())),
                    )

    def related_objects(self, related_model, related_fields, objs):
        """
        Get a QuerySet of the related model to objs via related fields.
        """
        predicate = query_utils.Q(
            *((f"{related_field.name}__in", objs) for related_field in related_fields),
            _connector=query_utils.Q.OR,
        )
        return related_model._base_manager.using(self.using).filter(predicate)

    def instances_with_model(self):
        """
        Generates instances with their corresponding models.
        
        Yields:
        tuple: A tuple containing the model and an instance of that model.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the model and an instance of that model.
        
        Notes:
        - The function iterates over the 'data' dictionary, where keys are model names and values are lists of instances.
        - It yields tuples of (model, instance) for each instance in the data.
        """

        for model, instances in self.data.items():
            for obj in instances:
                yield model, obj

    def sort(self):
        """
        Sorts the models based on their dependencies.
        
        This function takes a list of models and sorts them according to their dependencies. It uses the `dependencies` attribute, which is a dictionary mapping each model's concrete model to a set of its dependencies. The function iteratively selects models that have no outstanding dependencies and adds them to the sorted list until all models are sorted. The sorted models are then assigned back to the `data` attribute.
        
        Args:
        None
        
        Returns:
        None
        """

        sorted_models = []
        concrete_models = set()
        models = list(self.data)
        while len(sorted_models) < len(models):
            found = False
            for model in models:
                if model in sorted_models:
                    continue
                dependencies = self.dependencies.get(model._meta.concrete_model)
                if not (dependencies and dependencies.difference(concrete_models)):
                    sorted_models.append(model)
                    concrete_models.add(model._meta.concrete_model)
                    found = True
            if not found:
                return
        self.data = {model: self.data[model] for model in sorted_models}

    def delete(self):
        """
        Delete instances from the database.
        
        This method processes the deletion of instances by sorting them, sending pre-delete signals, performing fast deletes, updating fields, and finally deleting the instances. It also handles post-delete signals and updates the state of the instances.
        
        Parameters:
        None (The method is called on an instance of a manager class).
        
        Returns:
        A tuple containing the total number of deleted objects and a dictionary mapping model labels to the number of deleted objects for each model.
        
        Important Functions
        """

        # sort instance collections
        for model, instances in self.data.items():
            self.data[model] = sorted(instances, key=attrgetter("pk"))

        # if possible, bring the models in an order suitable for databases that
        # don't support transactions or cannot defer constraint checks until the
        # end of a transaction.
        self.sort()
        # number of objects deleted for each model label
        deleted_counter = Counter()

        # Optimize for the case with a single obj and no dependencies
        if len(self.data) == 1 and len(instances) == 1:
            instance = list(instances)[0]
            if self.can_fast_delete(instance):
                with transaction.mark_for_rollback_on_error(self.using):
                    count = sql.DeleteQuery(model).delete_batch(
                        [instance.pk], self.using
                    )
                setattr(instance, model._meta.pk.attname, None)
                return count, {model._meta.label: count}

        with transaction.atomic(using=self.using, savepoint=False):
            # send pre_delete signals
            for model, obj in self.instances_with_model():
                if not model._meta.auto_created:
                    signals.pre_delete.send(
                        sender=model,
                        instance=obj,
                        using=self.using,
                        origin=self.origin,
                    )

            # fast deletes
            for qs in self.fast_deletes:
                count = qs._raw_delete(using=self.using)
                if count:
                    deleted_counter[qs.model._meta.label] += count

            # update fields
            for model, instances_for_fieldvalues in self.field_updates.items():
                for (field, value), instances in instances_for_fieldvalues.items():
                    query = sql.UpdateQuery(model)
                    query.update_batch(
                        [obj.pk for obj in instances], {field.name: value}, self.using
                    )

            # reverse instance collections
            for instances in self.data.values():
                instances.reverse()

            # delete instances
            for model, instances in self.data.items():
                query = sql.DeleteQuery(model)
                pk_list = [obj.pk for obj in instances]
                count = query.delete_batch(pk_list, self.using)
                if count:
                    deleted_counter[model._meta.label] += count

                if not model._meta.auto_created:
                    for obj in instances:
                        signals.post_delete.send(
                            sender=model,
                            instance=obj,
                            using=self.using,
                            origin=self.origin,
                        )

        # update collected instances
        for instances_for_fieldvalues in self.field_updates.values():
            for (field, value), instances in instances_for_fieldvalues.items():
                for obj in instances:
                    setattr(obj, field.attname, value)
        for model, instances in self.data.items():
            for instance in instances:
                setattr(instance, model._meta.pk.attname, None)
        return sum(deleted_counter.values()), dict(deleted_counter)
