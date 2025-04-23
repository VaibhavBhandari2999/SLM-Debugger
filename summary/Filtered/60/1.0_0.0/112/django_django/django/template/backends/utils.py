from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a Django web application.
    
    Args:
    request (HttpRequest): The current request object from Django.
    
    Returns:
    str: A string containing the HTML code for a hidden input field with the CSRF token.
    
    This function is used to include a CSRF token in a form, which helps protect against CSRF attacks.
    The CSRF token is generated using the `get_token` function, which is not shown here but is assumed to be a part
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request),
    )


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
