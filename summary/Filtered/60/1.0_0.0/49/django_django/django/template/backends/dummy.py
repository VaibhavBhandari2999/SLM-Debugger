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
        Initializes a new instance of a class.
        
        Parameters:
        params (dict): A dictionary containing initialization parameters. The dictionary is expected to contain a 'OPTIONS' key, which may contain additional options that are not recognized by the class.
        
        This method first makes a copy of the provided parameters to avoid modifying the original dictionary. It then extracts the 'OPTIONS' key from the parameters and checks if it contains any unrecognized options. If there are any unrecognized options, it raises an `ImproperlyConfigured
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
        """
        Retrieve a template based on the given template name.
        
        Parameters:
        template_name (str): The name of the template to retrieve.
        
        Returns:
        Template: The template object if found, otherwise raises TemplateDoesNotExist.
        
        Raises:
        TemplateDoesNotExist: If the template cannot be found among the tried files.
        
        This function attempts to find and read a template file based on the provided template name. It iterates over possible filenames, tries to open each one, and returns the template if successful. If a
        """

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
        request (HttpRequest, optional): The HTTP request object, used to generate CSRF tokens.
        
        Returns:
        str: The rendered template as a string.
        
        Key Points:
        - If `context` is not provided, an empty dictionary is used
        """

        if context is None:
            context = {}
        else:
            context = {k: conditional_escape(v) for k, v in context.items()}
        if request is not None:
            context['csrf_input'] = csrf_input_lazy(request)
            context['csrf_token'] = csrf_token_lazy(request)
        return self.safe_substitute(context)
