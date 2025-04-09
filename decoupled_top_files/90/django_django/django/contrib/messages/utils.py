"""
The provided Python file is part of a Django application and is responsible for defining and returning message level tags used for displaying messages with different severity levels. It leverages Django's built-in `constants` module and the project's settings to customize these tags.

#### Classes:
None

#### Functions:
1. **get_level_tags()**: This function combines the default message level tags from Django's `constants` module with any custom tags defined in the project's settings under the `MESSAGE_TAGS` key. It returns a dictionary mapping message levels to their corresponding tags.

#### Key Responsibilities:
- Customizing message display levels based on project-specific configurations.
- Ensuring consistent and customizable message handling across the application.

#### Interactions:
- The function interacts with Django's
"""
from django.conf import settings
from django.contrib.messages import constants


def get_level_tags():
    """
    Return the message level tags.
    """
    return {
        **constants.DEFAULT_TAGS,
        **getattr(settings, 'MESSAGE_TAGS', {}),
    }
