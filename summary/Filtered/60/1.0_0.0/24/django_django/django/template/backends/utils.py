from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a Django web application.
    
    This function creates an HTML input field that is used to protect web applications against CSRF attacks. The input field is hidden and contains a CSRF token, which is a unique identifier for the user's session.
    
    Parameters:
    request (HttpRequest): The Django HttpRequest object representing the current request.
    
    Returns:
    str: A string containing the HTML code for the CSRF input field.
    
    Key Points:
    - The CSRF
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request))


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
