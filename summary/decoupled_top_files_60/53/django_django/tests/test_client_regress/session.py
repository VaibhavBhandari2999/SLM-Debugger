from django.contrib.sessions.backends.base import SessionBase


class SessionStore(SessionBase):
    """
    A simple cookie-based session storage implementation.

    The session key is actually the session data, pickled and encoded.
    This means that saving the session will change the session key.
    """
    def __init__(self, session_key=None):
        super().__init__(session_key)

    def exists(self, session_key):
        return False

    def create(self):
        self._session_key = self.encode({})

    def save(self, must_create=False):
        self._session_key = self.encode(self._session)

    def delete(self, session_key=None):
        self._session_key = self.encode({})

    def load(self):
        """
        Loads the session data.
        
        This method attempts to decode the session data using the session key. If decoding fails, it sets the `modified` attribute to True and returns an empty dictionary.
        
        Parameters:
        None
        
        Returns:
        dict: The decoded session data or an empty dictionary if decoding fails.
        
        Raises:
        Exception: If there is an error during decoding.
        """

        try:
            return self.decode(self.session_key)
        except Exception:
            self.modified = True
            return {}
