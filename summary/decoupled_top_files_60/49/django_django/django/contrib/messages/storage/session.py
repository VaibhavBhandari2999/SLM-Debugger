import json

from django.contrib.messages.storage.base import BaseStorage
from django.contrib.messages.storage.cookie import (
    MessageDecoder, MessageEncoder,
)


class SessionStorage(BaseStorage):
    """
    Store messages in the session (that is, django.contrib.sessions).
    """
    session_key = '_messages'

    def __init__(self, request, *args, **kwargs):
        assert hasattr(request, 'session'), "The session-based temporary "\
            "message storage requires session middleware to be installed, "\
            "and come before the message middleware in the "\
            "MIDDLEWARE list."
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
        encoder = MessageEncoder(separators=(',', ':'))
        return encoder.encode(messages)

    def deserialize_messages(self, data):
        """
        Deserialize messages from a given string.
        
        Args:
        data (str): The string containing serialized messages.
        
        Returns:
        dict or list: The deserialized messages as a dictionary or list, or the original data if it is not a string.
        
        Notes:
        - If the input data is a string, it will be deserialized using `json.loads` with the `MessageDecoder` class.
        - If the input data is not a string, it will be returned as is.
        """

        if data and isinstance(data, str):
            return json.loads(data, cls=MessageDecoder)
        return data
ssages)

    def deserialize_messages(self, data):
        if data and isinstance(data, str):
            return json.loads(data, cls=MessageDecoder)
        return data
