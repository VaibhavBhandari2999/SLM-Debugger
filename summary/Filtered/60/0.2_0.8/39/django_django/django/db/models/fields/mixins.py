from django.core import checks

NOT_PROVIDED = object()


class FieldCacheMixin:
    """Provide an API for working with the model's fields value cache."""

    def get_cache_name(self):
        raise NotImplementedError

    def get_cached_value(self, instance, default=NOT_PROVIDED):
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
        Checks if the field has a default value and if it is not callable. If the default is not callable, returns a warning indicating that the default should be a callable to avoid sharing between instances. If the default is callable or the field does not have a default, returns an empty list. The function returns a list of warnings.
        
        Parameters:
        - self (Field): The field object to check.
        
        Returns:
        - list: A list of warnings if the default is not callable, otherwise an empty list.
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
        Checks the configuration for errors.
        
        This method extends the functionality of the base class's `check` method by first validating the configuration using the base class's `check` method and then running additional default checks. It returns a list of errors found during the validation process.
        
        Parameters:
        **kwargs: Additional keyword arguments passed to the base class's `check` method.
        
        Returns:
        list: A list of error messages indicating any issues found during the validation process.
        """

        errors = super().check(**kwargs)
        errors.extend(self._check_default())
        return errors
