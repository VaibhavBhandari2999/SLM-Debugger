import string

from django.core.exceptions import ImproperlyConfigured
from django.template import Origin, TemplateDoesNotExist
from django.utils.html import conditional_escape

from .base import BaseEngine
from .utils import csrf_input_lazy, csrf_token_lazy


class TemplateStrings(BaseEngine):

    app_dirname = "template_strings"

    def __init__(self, params):
        """
        Initialize the object with provided parameters.
        
        Parameters:
        params (dict): A dictionary containing initialization parameters. The dictionary is expected to have a key 'OPTIONS' which may contain additional parameters. If 'OPTIONS' contains any unknown parameters, an ImproperlyConfigured exception is raised.
        
        Returns:
        None: This method does not return any value. It is used to set up the object with the given parameters.
        
        Raises:
        ImproperlyConfigured: If the 'OPTIONS' dictionary contains any unknown
        """

        params = params.copy()
        options = params.pop("OPTIONS").copy()
        if options:
            raise ImproperlyConfigured("Unknown options: {}".format(", ".join(options)))
        super().__init__(params)

    def from_string(self, template_code):
        return Template(template_code)

    def get_template(self, template_name):
        """
        Retrieve a template by name.
        
        Parameters:
        template_name (str): The name of the template to retrieve.
        
        Returns:
        Template: The template object if found.
        
        Raises:
        TemplateDoesNotExist: If the template does not exist and tried list is populated with failed attempts.
        
        This function attempts to find and load a template file by the given name. It tries multiple filenames by calling `iter_template_filenames`. If the file is not found, it records the failure and tries the next filename. If all
        """

        tried = []
        for template_file in self.iter_template_filenames(template_name):
            try:
                with open(template_file, encoding="utf-8") as fp:
                    template_code = fp.read()
            except FileNotFoundError:
                tried.append(
                    (
                        Origin(template_file, template_name, self),
                        "Source does not exist",
                    )
                )
            else:
                return Template(template_code)
        raise TemplateDoesNotExist(template_name, tried=tried, backend=self)


class Template(string.Template):
    def render(self, context=None, request=None):
        """
        Renders the template with the given context and request.
        
        Parameters:
        context (dict, optional): A dictionary of variables to be used in rendering the template. If not provided, an empty dictionary is used. The values in the dictionary are escaped to prevent XSS attacks.
        request (HttpRequest, optional): The current HTTP request object. If provided, it is used to generate CSRF tokens for the template context.
        
        Returns:
        str: The rendered template as a string.
        
        This function takes a template and
        """

        if context is None:
            context = {}
        else:
            context = {k: conditional_escape(v) for k, v in context.items()}
        if request is not None:
            context["csrf_input"] = csrf_input_lazy(request)
            context["csrf_token"] = csrf_token_lazy(request)
        return self.safe_substitute(context)
