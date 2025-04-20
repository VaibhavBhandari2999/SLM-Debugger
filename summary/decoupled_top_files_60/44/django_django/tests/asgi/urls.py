from django.http import FileResponse, HttpResponse
from django.urls import path


def hello(request):
    name = request.GET.get('name') or 'World'
    return HttpResponse('Hello %s!' % name)


def hello_meta(request):
    """
    Generate an HTTP response with a greeting message based on the HTTP referer and content type from the request's META dictionary.
    
    Parameters:
    - request (HttpRequest): The HTTP request object containing the necessary information.
    
    Returns:
    - HttpResponse: An HTTP response object with a greeting message and the content type from the request.
    
    Key Parameters:
    - request.META.get('HTTP_REFERER'): The URL of the previous page (HTTP referer).
    - request.META.get('CONTENT_TYPE'): The content type of the request.
    """

    return HttpResponse(
        'From %s' % request.META.get('HTTP_REFERER') or '',
        content_type=request.META.get('CONTENT_TYPE'),
    )


test_filename = __file__


urlpatterns = [
    path('', hello),
    path('file/', lambda x: FileResponse(open(test_filename, 'rb'))),
    path('meta/', hello_meta),
]
