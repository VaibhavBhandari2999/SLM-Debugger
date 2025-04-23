from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF input field for a Django web application.
    
    This function creates an HTML input element for CSRF protection, which is essential for preventing Cross-Site Request Forgery attacks.
    
    Parameters:
    request (HttpRequest): The Django request object containing the CSRF token.
    
    Returns:
    str: A formatted HTML string representing a hidden input field for CSRF protection.
    
    Example:
    >>> csrf_input(request)
    '<input type="hidden" name="csrfmiddlewaretoken" value="your_token_here">'
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request),
    )


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
