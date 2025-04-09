"""
This Python file provides utilities for handling Django template engines. It defines a class `EngineHandler` which processes and manages template engine configurations. The `EngineHandler` class includes methods to initialize and retrieve template engines based on their aliases. Additionally, it includes a utility function `get_app_template_dirs` to discover and return paths of directories containing application templates. The file ensures that template engine configurations are properly validated and that each engine has a unique alias. The `EngineHandler` class uses caching mechanisms to optimize performance when accessing template engines multiple times. ```python
"""
import functools
from collections import Counter
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from django.utils.module_loading import import_string


class InvalidTemplateEngineError(ImproperlyConfigured):
    pass


class EngineHandler:
    def __init__(self, templates=None):
        """
        templates is an optional list of template engine definitions
        (structured like settings.TEMPLATES).
        """
        self._templates = templates
        self._engines = {}

    @cached_property
    def templates(self):
        """
        Retrieve and process template configurations.
        
        This method checks if the `_templates` attribute is None, and if so, initializes it with the value of `settings.TEMPLATES`. It then processes each template configuration by extracting the backend name, creating a new dictionary with specific keys, and storing it in the `templates` dictionary. The method also ensures that each template engine has a unique alias by checking for duplicates. Finally, it returns the processed templates.
        
        :return: A dictionary containing processed template configurations
        """

        if self._templates is None:
            self._templates = settings.TEMPLATES

        templates = {}
        backend_names = []
        for tpl in self._templates:
            try:
                # This will raise an exception if 'BACKEND' doesn't exist or
                # isn't a string containing at least one dot.
                default_name = tpl["BACKEND"].rsplit(".", 2)[-2]
            except Exception:
                invalid_backend = tpl.get("BACKEND", "<not defined>")
                raise ImproperlyConfigured(
                    "Invalid BACKEND for a template engine: {}. Check "
                    "your TEMPLATES setting.".format(invalid_backend)
                )

            tpl = {
                "NAME": default_name,
                "DIRS": [],
                "APP_DIRS": False,
                "OPTIONS": {},
                **tpl,
            }

            templates[tpl["NAME"]] = tpl
            backend_names.append(tpl["NAME"])

        counts = Counter(backend_names)
        duplicates = [alias for alias, count in counts.most_common() if count > 1]
        if duplicates:
            raise ImproperlyConfigured(
                "Template engine aliases aren't unique, duplicates: {}. "
                "Set a unique NAME for each engine in settings.TEMPLATES.".format(
                    ", ".join(duplicates)
                )
            )

        return templates

    def __getitem__(self, alias):
        """
        Retrieve the template engine with the specified alias.
        
        Args:
        alias (str): The alias of the template engine to retrieve.
        
        Returns:
        Engine: The template engine instance corresponding to the given alias.
        
        Raises:
        InvalidTemplateEngineError: If the specified alias is not found in the settings.TEMPLATES configuration.
        
        Summary:
        This method retrieves the template engine with the specified alias from the internal `_engines` dictionary. If the alias is not found, it attempts to load
        """

        try:
            return self._engines[alias]
        except KeyError:
            try:
                params = self.templates[alias]
            except KeyError:
                raise InvalidTemplateEngineError(
                    "Could not find config for '{}' "
                    "in settings.TEMPLATES".format(alias)
                )

            # If importing or initializing the backend raises an exception,
            # self._engines[alias] isn't set and this code may get executed
            # again, so we must preserve the original params. See #24265.
            params = params.copy()
            backend = params.pop("BACKEND")
            engine_cls = import_string(backend)
            engine = engine_cls(params)

            self._engines[alias] = engine
            return engine

    def __iter__(self):
        return iter(self.templates)

    def all(self):
        return [self[alias] for alias in self]


@functools.lru_cache
def get_app_template_dirs(dirname):
    """
    Return an iterable of paths of directories to load app templates from.

    dirname is the name of the subdirectory containing templates inside
    installed applications.
    """
    template_dirs = [
        Path(app_config.path) / dirname
        for app_config in apps.get_app_configs()
        if app_config.path and (Path(app_config.path) / dirname).is_dir()
    ]
    # Immutable return value because it will be cached and shared by callers.
    return tuple(template_dirs)
