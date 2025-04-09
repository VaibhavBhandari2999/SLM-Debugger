from django.conf import settings
from django.contrib.sessions.backends.base import (
    CreateError, SessionBase, UpdateError,
)
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
        
        Args:
        None
        
        Returns:
        dict: The loaded session data or an empty dictionary if no valid session data is found.
        
        Raises:
        Exception: If there is an error retrieving the session data from the cache.
        
        Important Functions:
        - `_cache.get`: Retrieves the session data from the cache using the `cache_key`.
        - `self._session_key`: Sets the session key to `None` if no valid session data
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
        """
        Attempts to create a new session by generating a unique session key and saving it. If the cache fails, it retries up to 10,000 times before raising a `RuntimeError`. The function uses `_get_new_session_key` to generate a new session key and `save` with `must_create=True` to ensure a new session is created. If successful, it sets the `modified` attribute to `True`.
        
        Args:
        None
        
        Returns:
        None
        """

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
            "It is likely that the cache is unavailable.")

    def save(self, must_create=False):
        """
        Saves the session data to the cache.
        
        Args:
        must_create (bool): If True, creates a new entry in the cache even if one already exists.
        
        Returns:
        bool: True if the session was successfully saved, False if it was not created due to existing entry.
        
        Raises:
        UpdateError: If the session cannot be updated because an entry already exists and `must_create` is False.
        CreateError: If the session cannot be created because the cache operation failed
        """

        if self.session_key is None:
            return self.create()
        if must_create:
            func = self._cache.add
        elif self._cache.get(self.cache_key) is not None:
            func = self._cache.set
        else:
            raise UpdateError
        result = func(self.cache_key,
                      self._get_session(no_load=must_create),
                      self.get_expiry_age())
        if must_create and not result:
            raise CreateError

    def exists(self, session_key):
        return bool(session_key) and (self.cache_key_prefix + session_key) in self._cache

    def delete(self, session_key=None):
        """
        Deletes a session from the cache.
        
        Args:
        session_key (str, optional): The session key to delete. If not provided, uses the current session key.
        
        Returns:
        None
        
        This function deletes a session from the cache using the provided or current session key.
        """

        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        self._cache.delete(self.cache_key_prefix + session_key)

    @classmethod
    def clear_expired(cls):
        pass
