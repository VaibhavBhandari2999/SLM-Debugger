"""
```markdown
This Python script contains a Django-specific decorator `staff_member_required` which ensures that only authenticated and staff members can access certain views. It leverages Django's built-in `user_passes_test` decorator to perform the check. The script does not define any additional classes but focuses on providing a reusable function for securing views in Django applications.
```

Your summary looks good! Here's a slightly refined version with a bit more detail:

```markdown
This Python script contains a Django-specific decorator `staff_member_required` which ensures that only authenticated and staff members can access certain views. It leverages Django's built-in `user_passes_test` decorator to perform the check. The script does not define any additional classes but focuses on providing a
"""
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def staff_member_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME,
                          login_url='admin:login'):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
