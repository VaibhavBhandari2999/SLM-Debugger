from django.core import checks

NOT_PROVIDED = object()


class FieldCacheMixin:
    """Provide an API for working with the model's fields value cache."""

    def get_cache_name(self):
        raise NotImplementedError

    def get_cached_value(self, instance, default=NOT_PROVIDED):
        """
        Retrieve a cached value for an instance.
        
        This method fetches a cached value from the instance's fields_cache dictionary using a generated cache name. If the value is not found in the cache, and a default value is not provided, a KeyError is raised.
        
        Parameters:
        instance (object): The instance from which to retrieve the cached value.
        default (Any, optional): The default value to return if the cache is empty. If not provided and the cache is empty, a KeyError is raised.
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
        Function to check if the field has a default value and if it is not callable.
        
        This function checks whether the field has a default value and if that default value is not a callable. If the default value is not callable, it returns a warning indicating that the default should be a callable to avoid shared instances between field instances. If the default value is callable or the field does not have a default value, it returns an empty list.
        
        Parameters:
        self (Field): The field instance to check.
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
        Checks for errors in the current object.
        
        This method extends the functionality of the base class's `check` method by adding additional validation checks.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments. These are passed to the base class's `check` method.
        
        Returns:
        list: A list of error messages. This list includes any errors from the base class's `check` method as well as any errors from the additional checks performed by this method.
        """

        errors = super().check(**kwargs)
        errors.extend(self._check_default())
        return errors
