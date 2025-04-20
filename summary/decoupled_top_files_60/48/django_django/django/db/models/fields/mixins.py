from django.core import checks

NOT_PROVIDED = object()


class FieldCacheMixin:
    """Provide an API for working with the model's fields value cache."""

    def get_cache_name(self):
        raise NotImplementedError

    def get_cached_value(self, instance, default=NOT_PROVIDED):
        """
        Retrieve a cached value for an instance.
        
        This method fetches a cached value from the instance's fields cache. If the value is not found, it raises a KeyError unless a default value is provided.
        
        Parameters:
        instance (object): The instance from which to retrieve the cached value.
        default (Any, optional): The default value to return if the cache is empty. If not provided and the cache is empty, a KeyError is raised.
        
        Returns:
        Any: The cached value if found,
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
        Checks the validation of the object.
        
        This method performs validation checks on the object. It first calls the `check` method of the superclass, passing any provided keyword arguments. Then, it appends the results of the `_check_default` method to the errors collected from the superclass. The method returns a list of errors.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments to be passed to the superclass's `check` method.
        
        Returns:
        list: A list of error messages indicating any validation failures.
        """

        errors = super().check(**kwargs)
        errors.extend(self._check_default())
        return errors
