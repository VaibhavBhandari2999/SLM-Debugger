"""
The provided Python file contains two classes: `FieldCacheMixin` and `CheckFieldDefaultMixin`. 

- `FieldCacheMixin`: This mixin provides methods for interacting with the model's fields value cache. It includes methods to get, check, set, and delete cached values. The `get_cache_name` method must be implemented by subclasses to specify the name of the cache entry.

- `CheckFieldDefaultMixin`: This mixin adds validation logic to ensure that the field's default value is a callable. It overrides the `check` method to perform additional checks on the default value and returns warnings if the default is not callable.

Both mixins are designed to be used as base classes for Django model fields, enhancing their functionality with caching and default value validation
"""
from django.core import checks

NOT_PROVIDED = object()


class FieldCacheMixin:
    """Provide an API for working with the model's fields value cache."""

    def get_cache_name(self):
        raise NotImplementedError

    def get_cached_value(self, instance, default=NOT_PROVIDED):
        """
        Retrieve a cached value for an instance.
        
        Args:
        instance (object): The instance from which to retrieve the cached value.
        default (optional): The default value to return if the cache is not found. If not provided, a KeyError will be raised.
        
        Returns:
        object: The cached value or the specified default value.
        
        Raises:
        KeyError: If the cache is not found and no default value is provided.
        
        Important Functions:
        - `instance._state.fields_cache`:
        """

        cache_name = self.get_cache_name()
        try:
            return instance._state.fields_cache[cache_name]
        except KeyError:
            if default is NOT_PROVIDED:
                raise
            return default

    def is_cached(self, instance):
        return self.get_cache_name() in instance._state.fields_cache

    def set_cached_value(self, instance, value):
        instance._state.fields_cache[self.get_cache_name()] = value

    def delete_cached_value(self, instance):
        del instance._state.fields_cache[self.get_cache_name()]


class CheckFieldDefaultMixin:
    _default_hint = ('<valid default>', '<invalid default>')

    def _check_default(self):
        """
        Checks if the field has a default value that is not callable. If so, returns a warning indicating that the default should be a callable. Otherwise, returns an empty list.
        
        Args:
        self: The current instance of the class.
        
        Returns:
        A list containing a `Warning` object if the default is not callable, otherwise an empty list.
        """

        if self.has_default() and self.default is not None and not callable(self.default):
            return [
                checks.Warning(
                    "%s default should be a callable instead of an instance "
                    "so that it's not shared between all field instances." % (
                        self.__class__.__name__,
                    ),
                    hint=(
                        'Use a callable instead, e.g., use `%s` instead of '
                        '`%s`.' % self._default_hint
                    ),
                    obj=self,
                    id='fields.E010',
                )
            ]
        else:
            return []

    def check(self, **kwargs):
        """
        Checks the provided keyword arguments and returns a list of errors.
        
        Args:
        **kwargs: Keyword arguments to be checked.
        
        Returns:
        A list of errors (strings) resulting from the checks performed.
        """

        errors = super().check(**kwargs)
        errors.extend(self._check_default())
        return errors
