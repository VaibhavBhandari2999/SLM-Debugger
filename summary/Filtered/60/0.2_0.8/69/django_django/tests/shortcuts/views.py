from django.shortcuts import render


def render_view(request):
    return render(request, 'shortcuts/render_test.html', {
        'foo': 'FOO',
        'bar': 'BAR',
    })


def render_view_with_multiple_templates(request):
    """
    Render a view using multiple templates.
    
    This function renders a view by using multiple templates and passes a context to them.
    
    Parameters:
    request (HttpRequest): The HTTP request object.
    
    Returns:
    HttpResponse: The rendered HTTP response containing the result of rendering the templates.
    
    Template Usage:
    - The function attempts to render 'shortcuts/no_such_template.html' first.
    - If the first template does not exist, it falls back to rendering 'shortcuts/render_test.html'.
    - The context passed
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
