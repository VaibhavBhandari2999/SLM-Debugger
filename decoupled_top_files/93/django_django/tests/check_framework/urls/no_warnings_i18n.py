"""
```markdown
# This file configures URL patterns for an internationalized Django application.
# It sets up URL patterns using `i18n_patterns` which automatically handles language
# prefixes based on the current user's language preference. The only pattern defined
# here is a placeholder that translates the "translated/" path into the user's preferred
# language and returns the request object unchanged.

# Main components:
# - `i18n_patterns`: A utility function from Django's URL configuration that adds
#   language prefixes to URL patterns.
# - `path`: A function used to define URL patterns.
# - `_`: A translation function from Django's localization utilities.

# Key logic:
# - Translates the "translated/" path
"""
from django.conf.urls.i18n import i18n_patterns
from django.urls import path
from django.utils.translation import gettext_lazy as _

urlpatterns = i18n_patterns(
    path(_("translated/"), lambda x: x, name="i18n_prefixed"),
)
