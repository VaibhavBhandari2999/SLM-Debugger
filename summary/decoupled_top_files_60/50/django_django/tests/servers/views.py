from urllib.request import urlopen

from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Person


def example_view(request):
    return HttpResponse('example view')


def streaming_example_view(request):
    return StreamingHttpResponse((b'I', b'am', b'a', b'stream'))


def model_view(request):
    people = Person.objects.all()
    return HttpResponse('\n'.join(person.name for person in people))


def create_model_instance(request):
    """
    Creates a new model instance for a person.
    
    This function initializes a new instance of the Person model with the name 'emily', saves it to the database, and returns an HTTP response.
    
    Parameters:
    request (HttpRequest): The HTTP request object, although it is not used in this function.
    
    Returns:
    HttpResponse: An HTTP response object indicating the success of the operation.
    """

    person = Person(name='emily')
    person.save()
    return HttpResponse()


def environ_view(request):
    return HttpResponse("\n".join("%s: %r" % (k, v) for k, v in request.environ.items()))


def subview(request):
    return HttpResponse('subview')


def subview_calling_view(request):
    with urlopen(request.GET['url'] + '/subview/') as response:
        return HttpResponse('subview calling view: {}'.format(response.read().decode()))


def check_model_instance_from_subview(request):
    """
    Function: check_model_instance_from_subview
    Summary: This function checks if a model instance can be created from a subview by making HTTP requests to specified URLs.
    
    Parameters:
    - request: An HttpRequest object containing the URL parameters needed to make the HTTP requests.
    
    Returns:
    - An HttpResponse object with a string indicating whether the subview successfully called the view.
    
    Key Parameters:
    - url: A string representing the base URL for the model instance creation and view.
    
    Notes:
    - The function makes two HTTP
    """

    with urlopen(request.GET['url'] + '/create_model_instance/'):
        pass
    with urlopen(request.GET['url'] + '/model_view/') as response:
        return HttpResponse('subview calling view: {}'.format(response.read().decode()))


@csrf_exempt
def method_view(request):
    return HttpResponse(request.method)
