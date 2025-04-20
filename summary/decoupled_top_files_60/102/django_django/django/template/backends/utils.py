from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a Django web application.
    
    This function creates an HTML input field for CSRF protection, which is essential for securing web applications against CSRF attacks.
    
    Args:
    request (HttpRequest): The Django request object containing the CSRF token.
    
    Returns:
    str: A formatted HTML string representing the CSRF input field.
    
    Example:
    >>> csrf_input(request)
    '<input type="hidden" name="csrfmiddlewaretoken" value="your_token_value">'
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request),
    )


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
