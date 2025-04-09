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
    Generate an HTML form using Django's form and template rendering functionalities.
    
    Args:
    request: The HTTP request object.
    
    Returns:
    An HttpResponse object containing the rendered HTML form.
    
    Summary:
    This function creates a Django form with a single FloatField, renders it using a Django template, and returns an HttpResponse object.
    """

    class Form(forms.Form):
        number = forms.FloatField()

    template = Template("<html>{{ form }}</html>")
    context = Context({"form": Form()})
    return HttpResponse(template.render(context))
