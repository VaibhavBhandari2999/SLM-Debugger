from django.conf import settings
from django.contrib.sessions.backends.base import CreateError, SessionBase, UpdateError
from django.core.cache import caches

KEY_PREFIX = "django.contrib.sessions.cache"


class SessionStore(SessionBase):
    """
    A cache-based session store.
    """

    cache_key_prefix = KEY_PREFIX

    def __init__(self, session_key=None):
        self._cache = caches[settings.SESSION_CACHE_ALIAS]
        super().__init__(session_key)

    @property
    def cache_key(self):
        return self.cache_key_prefix + self._get_or_create_session_key()

    def load(self):
        """
        Loads the session data from the cache.
        
        This method attempts to retrieve session data from the cache using the session's cache key. If the retrieval fails due to an exception (e.g., an invalid cache key), it resets the session to ensure proper handling. If the session data is successfully retrieved, it is returned; otherwise, an empty dictionary is returned.
        
        Parameters:
        None
        
        Returns:
        dict: The session data if found, otherwise an empty dictionary.
        """

        try:
            session_data = self._cache.get(self.cache_key)
        except Exception:
            # Some backends (e.g. memcache) raise an exception on invalid
            # cache keys. If this happens, reset the session. See #17810.
            session_data = None
        if session_data is not None:
            return session_data
        self._session_key = None
        return {}

    def create(self):
        # Because a cache can fail silently (e.g. memcache), we don't know if
        # we are failing to create a new session because of a key collision or
        # because the cache is missing. So we try for a (large) number of times
        # and then raise an exception. That's the risk you shoulder if using
        # cache backing.
        for i in range(10000):
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return
        raise RuntimeError(
            "Unable to create a new session key. "
            "It is likely that the cache is unavailable."
        )

    def save(self, must_create=False):
        """
        Saves the session to the cache.
        
        Args:
        must_create (bool, optional): If True, the session will be created if it does not exist. Defaults to False.
        
        Returns:
        bool: True if the session was successfully saved, False if it was not (e.g., due to a conflict).
        
        Raises:
        UpdateError: If the session already exists and must_create is False.
        CreateError: If the session could not be created when must_create is True.
        
        This function checks
        """

        if self.session_key is None:
            return self.create()
        if must_create:
            func = self._cache.add
        elif self._cache.get(self.cache_key) is not None:
            func = self._cache.set
        else:
            raise UpdateError
        result = func(
            self.cache_key,
            self._get_session(no_load=must_create),
            self.get_expiry_age(),
        )
        if must_create and not result:
            raise CreateError

    def exists(self, session_key):
        return (
            bool(session_key) and (self.cache_key_prefix + session_key) in self._cache
        )

    def delete(self, session_key=None):
        """
        Delete a session from the cache.
        
        This method removes a session from the cache based on the provided session key. If no session key is provided, it uses the session's internal session key. The session key is prefixed with 'cache_key_prefix' before deletion.
        
        Parameters:
        session_key (str, optional): The session key to delete. If not provided, the session's internal session key is used.
        
        Returns:
        None: This method does not return any value. It simply deletes the session from
        """

        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        self._cache.delete(self.cache_key_prefix + session_key)

    @classmethod
    def clear_expired(cls):
        pass
