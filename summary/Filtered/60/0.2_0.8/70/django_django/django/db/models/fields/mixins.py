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
        default (Any, optional): The default value to return if the cache is not found. If not provided and the cache is not found, a KeyError will be raised. Defaults to NOT_PROVIDED.
        
        Returns:
        Any: The cached value if found, otherwise the provided default value or raises KeyError if default is not provided and cache is not found.
        
        Raises:
        KeyError
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
        Checks for validation errors.
        
        This method extends the validation process by first calling the parent class's check method with the provided keyword arguments (`**kwargs`). It then appends any additional errors from the `_check_default` method. The function returns a list of errors.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments passed to the parent class's check method.
        
        Returns:
        list: A list of validation errors.
        """

        errors = super().check(**kwargs)
        errors.extend(self._check_default())
        return errors
