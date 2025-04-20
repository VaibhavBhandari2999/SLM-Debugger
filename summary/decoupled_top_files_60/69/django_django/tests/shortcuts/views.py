from django.shortcuts import render


def render_view(request):
    """
    Render a template and return an HTTP response.
    
    This function takes a Django request object, a template name, and a context dictionary as input. It renders the specified template with the given context and returns an HTTP response.
    
    Parameters:
    request (HttpRequest): The Django request object.
    template_name (str): The name of the template to be rendered.
    context (dict): A dictionary containing the context variables to be passed to the template.
    
    Returns:
    HttpResponse: The rendered HTTP response containing the template
    """

    return render(request, 'shortcuts/render_test.html', {
        'foo': 'FOO',
        'bar': 'BAR',
    })


def render_view_with_multiple_templates(request):
    """
    Render a view using multiple templates.
    
    This function renders a Django view using multiple templates and passes context variables to them.
    
    Parameters:
    request (HttpRequest): The HTTP request object.
    
    Returns:
    HttpResponse: The rendered HTTP response containing the output of the templates.
    
    Template Usage:
    The function attempts to render the templates in the order provided. If the first template does not exist, it falls back to the second one. Context variables 'foo' and 'bar' are passed to both templates.
    """

    return render(request, [
        'shortcuts/no_such_template.html',
        'shortcuts/render_test.html',
    ], {
        'foo': 'FOO',
        'bar': 'BAR',
    })


def render_view_with_content_type(request):
    return render(request, 'shortcuts/render_test.html', {
        'foo': 'FOO',
        'bar': 'BAR',
    }, content_type='application/x-rendertest')


def render_view_with_status(request):
    return render(request, 'shortcuts/render_test.html', {
        'foo': 'FOO',
        'bar': 'BAR',
    }, status=403)


def render_view_with_using(request):
    using = request.GET.get('using')
    return render(request, 'shortcuts/using.html', using=using)
