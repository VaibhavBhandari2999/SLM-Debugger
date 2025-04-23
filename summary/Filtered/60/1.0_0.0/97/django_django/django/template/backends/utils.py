from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a web form.
    
    This function creates an HTML input element for CSRF protection. It is typically used in web forms to ensure that the request is made from the same origin as the form.
    
    Parameters:
    request (HttpRequest): The current HTTP request object.
    
    Returns:
    str: A formatted HTML string containing a hidden input field for CSRF token.
    
    Example:
    >>> csrf_input(request)
    '<input type="hidden" name="
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request),
    )


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
