from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a web form.
    
    This function creates an HTML input field for CSRF protection. The input field is hidden and is used to verify that the request is made by a user who has previously interacted with the site.
    
    Parameters:
    request (HttpRequest): The current HTTP request object.
    
    Returns:
    str: A formatted HTML string representing the CSRF input field.
    
    Key Parameters:
    request: The HTTP request object which contains the CSRF token
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request))


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
