import json

from django.contrib.messages.storage.base import BaseStorage
from django.contrib.messages.storage.cookie import (
    MessageDecoder, MessageEncoder,
)
from django.core.exceptions import ImproperlyConfigured


class SessionStorage(BaseStorage):
    """
    Store messages in the session (that is, django.contrib.sessions).
    """
    session_key = '_messages'

    def __init__(self, request, *args, **kwargs):
        if not hasattr(request, 'session'):
            raise ImproperlyConfigured(
                'The session-based temporary message storage requires session '
                'middleware to be installed, and come before the message '
                'middleware in the MIDDLEWARE list.'
            )
        super().__init__(request, *args, **kwargs)

    def _get(self, *args, **kwargs):
        """
        Retrieve a list of messages from the request's session. This storage
        always stores everything it is given, so return True for the
        all_retrieved flag.
        """
        return self.deserialize_messages(self.request.session.get(self.session_key)), True

    def _store(self, messages, response, *args, **kwargs):
        """
        Store a list of messages to the request's session.
        """
        if messages:
            self.request.session[self.session_key] = self.serialize_messages(messages)
        else:
            self.request.session.pop(self.session_key, None)
        return []

    def serialize_messages(self, messages):
        encoder = MessageEncoder()
        return encoder.encode(messages)

    def deserialize_messages(self, data):
        """
        Deserialize messages from a given string of JSON data.
        
        Args:
        data (str): The JSON string to be deserialized.
        
        Returns:
        dict or list: The deserialized data if input is a valid JSON string, otherwise returns the original data.
        
        Notes:
        - The function checks if the input data is a non-empty string.
        - It uses the `json.loads` method to parse the JSON string.
        - The `MessageDecoder` class is used as the decoding strategy for the JSON
        """

        if data and isinstance(data, str):
            return json.loads(data, cls=MessageDecoder)
        return data
loads(data, cls=MessageDecoder)
        return data
