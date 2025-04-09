"""
```markdown
This Python script provides a custom Django message storage backend that stores messages in the session. It includes a `SessionStorage` class which handles serialization and deserialization of messages using JSON and interacts with Django's session framework. The class ensures that session middleware is properly configured before storing or retrieving messages.
```

### Detailed Docstring:
```python
"""
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
        """
        Initialize the MessageMiddleware.
        
        Args:
        request (HttpRequest): The HTTP request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Raises:
        ImproperlyConfigured: If session middleware is not installed or not
        placed before message middleware in MIDDLEWARE list.
        
        This method checks if the request object has a session attribute, and raises an error if it doesn't. It then calls the superclass's `__init__` method with
        """

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
        Deserialize messages from a given string.
        
        Args:
        data (str): The string containing serialized message data.
        
        Returns:
        dict or list: Deserialized message data represented as a dictionary or list.
        """

        if data and isinstance(data, str):
            return json.loads(data, cls=MessageDecoder)
        return data
