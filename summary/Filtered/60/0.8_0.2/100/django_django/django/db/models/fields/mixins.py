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
    _default_hint = ("<valid default>", "<invalid default>")

    def _check_default(self):
        if (
            self.has_default()
            and self.default is not None
            and not callable(self.default)
        ):
            return [
                checks.Warning(
                    "%s default should be a callable instead of an instance "
                    "so that it's not shared between all field instances."
                    % (self.__class__.__name__,),
                    hint=(
                        "Use a callable instead, e.g., use `%s` instead of "
                        "`%s`." % self._default_hint
                    ),
                    obj=self,
                    id="fields.E010",
                )
            ]
        else:
            return []

    def check(self, **kwargs):
        """
        Checks for errors in the current object.
        
        This method extends the functionality of the base class's `check` method by adding additional validation checks.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments. These are passed to the base class's `check` method and should be relevant to the specific validation checks required by the subclass.
        
        Returns:
        list: A list of error messages or validation errors. This list includes any errors from the base class's `check` method as well as any additional errors from the
        """

        errors = super().check(**kwargs)
        errors.extend(self._check_default())
        return errors
