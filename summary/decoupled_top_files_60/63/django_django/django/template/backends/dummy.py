import string

from django.core.exceptions import ImproperlyConfigured
from django.template import Origin, TemplateDoesNotExist
from django.utils.html import conditional_escape

from .base import BaseEngine
from .utils import csrf_input_lazy, csrf_token_lazy


class TemplateStrings(BaseEngine):

    app_dirname = 'template_strings'

    def __init__(self, params):
        """
        Initialize the object with the given parameters.
        
        Parameters:
        params (dict): A dictionary containing the parameters for initializing the object. The dictionary may include an 'OPTIONS' key with additional parameters, which will be ignored if present.
        
        Returns:
        None: This method does not return any value. It is used to set up the object with the provided parameters.
        
        Raises:
        ImproperlyConfigured: If the 'OPTIONS' key is present in the params dictionary and contains unknown options.
        """

        params = params.copy()
        options = params.pop('OPTIONS').copy()
        if options:
            raise ImproperlyConfigured(
                "Unknown options: {}".format(", ".join(options)))
        super().__init__(params)

    def from_string(self, template_code):
        return Template(template_code)

    def get_template(self, template_name):
        tried = []
        for template_file in self.iter_template_filenames(template_name):
            try:
                with open(template_file, encoding='utf-8') as fp:
                    template_code = fp.read()
            except FileNotFoundError:
                tried.append((
                    Origin(template_file, template_name, self),
                    'Source does not exist',
                ))
            else:
                return Template(template_code)
        raise TemplateDoesNotExist(template_name, tried=tried, backend=self)


class Template(string.Template):

    def render(self, context=None, request=None):
        """
        Renders the template with the given context and request.
        
        Parameters:
        context (dict, optional): A dictionary of variables to be used in the template. If not provided, an empty dictionary is used. The values in the dictionary are automatically escaped for security reasons.
        request (HttpRequest, optional): An HttpRequest object that provides access to the CSRF token and other request-related information.
        
        Returns:
        str: The rendered template as a string.
        
        This function takes a template and renders it with the provided context
        """

        if context is None:
            context = {}
        else:
            context = {k: conditional_escape(v) for k, v in context.items()}
        if request is not None:
            context['csrf_input'] = csrf_input_lazy(request)
            context['csrf_token'] = csrf_token_lazy(request)
        return self.safe_substitute(context)
