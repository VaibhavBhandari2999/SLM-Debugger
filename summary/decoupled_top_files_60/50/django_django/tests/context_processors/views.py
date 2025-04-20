from django.shortcuts import render

from .models import DebugObject


def request_processor(request):
    return render(request, 'context_processors/request_attrs.html')


def debug_processor(request):
    """
    Function: debug_processor
    Summary: A context processor function that provides debug objects for rendering in a template.
    Parameters:
    - request: The HTTP request object.
    Returns:
    A dictionary containing debug objects for rendering in a template.
    Details:
    This function is designed to be used as a context processor in Django. It retrieves debug objects from the database and passes them to the template for rendering. The function uses two different database connections ('default' and 'other') to fetch the debug objects.
    """

    context = {
        'debug_objects': DebugObject.objects,
        'other_debug_objects': DebugObject.objects.using('other'),
    }
    return render(request, 'context_processors/debug.html', context)
