"""
This Django app provides custom message handling for user notifications. It includes a custom message backend and utility functions for managing messages in views and templates.

### Classes and Functions:
1. **CustomMessageBackend**: A custom message backend class that extends `BaseStorage` from Django's message framework.
2. **get_messages**: A utility function that retrieves messages from the request context.
3. **add_message**: A utility function that adds a new message to the request context.

### Key Responsibilities:
- **CustomMessageBackend**: Handles storing and retrieving messages for the current request.
- **get_messages**: Fetches messages stored in the request context.
- **add_message**: Adds a new message to the request context with specified level, message text, and extra tags
"""
from django.contrib.messages.api import *  # NOQA
from django.contrib.messages.constants import *  # NOQA
