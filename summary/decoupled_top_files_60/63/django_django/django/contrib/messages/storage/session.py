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
        """
        Initialize the MessageMiddleware.
        
        Args:
        request (HttpRequest): The HTTP request object.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
        
        Raises:
        AssertionError: If the request object does not have a session attribute.
        
        This method is called during the initialization of the MessageMiddleware. It checks if the request object has a session attribute, which is necessary for the session-based temporary message storage. If the session attribute is missing, an AssertionError is raised.
        """

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
        encoder = MessageEncoder()
        return encoder.encode(messages)

    def deserialize_messages(self, data):
        """
        Deserialize messages from a given string of JSON data.
        
        Args:
        data (str): The JSON string containing serialized message data.
        
        Returns:
        dict or list: The deserialized data if input is a valid JSON string, otherwise returns the original input.
        
        Notes:
        - The function checks if the input data is a non-empty string.
        - It uses the `json.loads` method to parse the JSON string.
        - The `MessageDecoder` class is used as the decoding strategy for the JSON
        """

        if data and isinstance(data, str):
            return json.loads(data, cls=MessageDecoder)
        return data
