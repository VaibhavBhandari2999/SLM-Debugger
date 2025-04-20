from django.shortcuts import render

from .models import DebugObject


def request_processor(request):
    return render(request, 'context_processors/request_attrs.html')


def debug_processor(request):
    """
    Generates a context dictionary for debugging purposes.
    
    This function is designed to be used as a context processor in Django views. It fetches debug objects from the database and includes them in a context dictionary.
    
    Parameters:
    request (HttpRequest): The HTTP request object.
    
    Returns:
    dict: A context dictionary containing debug objects from the default and another database.
    
    Example:
    >>> debug_processor(request)
    {'debug_objects': <DebugObjectQuerySet>, 'other_debug_objects': <DebugObjectQuerySet>}
    """

    context = {
        'debug_objects': DebugObject.objects,
        'other_debug_objects': DebugObject.objects.using('other'),
    }
    return render(request, 'context_processors/debug.html', context)
