from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a web form.
    
    This function creates a hidden input field for CSRF protection, which is essential for securing web applications against CSRF attacks.
    
    Args:
    request (HttpRequest): The Django HttpRequest object representing the current request.
    
    Returns:
    str: A string containing the HTML code for the CSRF input field.
    
    Key Parameters:
    request: The request object is used to retrieve the CSRF token.
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request),
    )


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
