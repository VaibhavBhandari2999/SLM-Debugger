from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a web form.
    
    This function creates an HTML input element of type 'hidden' that includes a CSRF token for security purposes.
    
    Parameters:
    request (HttpRequest): The Django HttpRequest object that contains the CSRF token.
    
    Returns:
    str: A string containing the HTML code for the CSRF input field.
    
    Usage:
    This function is typically used in Django templates to include CSRF protection in form submissions.
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request),
    )


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
