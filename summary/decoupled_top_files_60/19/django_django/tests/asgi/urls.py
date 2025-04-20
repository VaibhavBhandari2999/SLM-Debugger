from django.http import FileResponse, HttpResponse
from django.urls import path


def hello(request):
    name = request.GET.get('name') or 'World'
    return HttpResponse('Hello %s!' % name)


def hello_meta(request):
    """
    Generate a response based on the HTTP referer and content type from the request.
    
    Parameters:
    request (HttpRequest): The incoming HTTP request object containing metadata such as HTTP referer and content type.
    
    Returns:
    HttpResponse: A response containing the HTTP referer or an empty string if not provided, with the content type from the request.
    
    This function is designed to return an HTTP response that includes the HTTP referer from the request metadata, or an empty string if the referer is not available. The content type
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
