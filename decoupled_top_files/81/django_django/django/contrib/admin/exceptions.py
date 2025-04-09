"""
The provided Python file is part of a Django application and is designed to handle security-related exceptions specifically related to the Django ModelAdmin interface. It defines two custom exception classes that are subclasses of `SuspiciousOperation`, which is a built-in Django exception for situations that match a potential security problem but don't fit anywhere else.

#### Classes Defined:
1. **DisallowedModelAdminLookup**: This class is raised when an invalid filter is passed to a Django ModelAdmin view via the URL querystring. It inherits from `SuspiciousOperation` and serves as a way to signal that the request contains a suspicious or unauthorized filter parameter.
2. **DisallowedModelAdminToField**: This class is raised when an invalid `to_field` is passed to a
"""
from django.core.exceptions import SuspiciousOperation


class DisallowedModelAdminLookup(SuspiciousOperation):
    """Invalid filter was passed to admin view via URL querystring"""
    pass


class DisallowedModelAdminToField(SuspiciousOperation):
    """Invalid to_field was passed to admin view via URL query string"""
    pass
