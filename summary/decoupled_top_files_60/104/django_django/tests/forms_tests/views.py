from django import forms
from django.http import HttpResponse
from django.template import Context, Template
from django.views.generic.edit import UpdateView

from .models import Article


class ArticleForm(forms.ModelForm):
    content = forms.CharField(strip=False, widget=forms.Textarea)

    class Meta:
        model = Article
        fields = "__all__"


class ArticleFormView(UpdateView):
    model = Article
    success_url = "/"
    form_class = ArticleForm


def form_view(request):
    """
    Generate a form view for a web page.
    
    This function creates a form with a single field 'number' of type float. It then renders this form within an HTML template and returns an HTTP response.
    
    Parameters:
    - request: The HTTP request object.
    
    Returns:
    - An HTTP response containing the rendered HTML form.
    
    Key Elements:
    - Form: A form class with a single field 'number' of type float.
    - Template: An HTML template that includes the form.
    - Context: A context object that
    """

    class Form(forms.Form):
        number = forms.FloatField()

    template = Template("<html>{{ form }}</html>")
    context = Context({"form": Form()})
    return HttpResponse(template.render(context))
