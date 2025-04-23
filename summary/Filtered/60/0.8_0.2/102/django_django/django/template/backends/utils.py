from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a Django web application.
    
    Args:
    request (HttpRequest): The current HTTP request object.
    
    Returns:
    str: A formatted HTML string containing a hidden input field for CSRF protection.
    
    Key Parameters:
    request (HttpRequest): The request object is used to retrieve the CSRF token.
    
    Notes:
    - The function uses `format_html` to safely format the HTML string.
    - `get_token(request)` is used to obtain the
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request),
    )


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
