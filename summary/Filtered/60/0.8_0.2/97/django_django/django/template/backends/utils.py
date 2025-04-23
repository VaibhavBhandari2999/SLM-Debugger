from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a Django web application.
    
    This function creates a hidden input field that is used to protect web applications against CSRF attacks. The input field is generated with a unique token that is specific to the user's session.
    
    Parameters:
    request (HttpRequest): The current request object from Django.
    
    Returns:
    str: A string containing the HTML code for the CSRF input field.
    
    Key Details:
    - The CSRF token is retrieved using the `
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request),
    )


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
