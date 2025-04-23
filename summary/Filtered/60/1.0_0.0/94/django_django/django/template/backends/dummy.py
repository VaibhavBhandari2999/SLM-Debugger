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
        Initialize the object with given parameters.
        
        Parameters:
        params (dict): A dictionary containing initialization parameters. The dictionary is expected to have a key 'OPTIONS' which may contain additional configuration options.
        
        This method initializes the object with the provided parameters. It first makes a copy of the 'params' dictionary to avoid modifying the original. It then extracts the 'OPTIONS' key from the dictionary and checks if there are any unknown options present. If any unknown options are found, it raises an ImproperlyConfig
        """

        params = params.copy()
        options = params.pop("OPTIONS").copy()
        if options:
            raise ImproperlyConfigured("Unknown options: {}".format(", ".join(options)))
        super().__init__(params)

    def from_string(self, template_code):
        return Template(template_code)

    def get_template(self, template_name):
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
        if context is None:
            context = {}
        else:
            context = {k: conditional_escape(v) for k, v in context.items()}
        if request is not None:
            context["csrf_input"] = csrf_input_lazy(request)
            context["csrf_token"] = csrf_token_lazy(request)
        return self.safe_substitute(context)
