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
        Any: The cached value if found, otherwise the provided default value.
        
        Raises:
        KeyError: If the cache is not found and no default value is provided
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
