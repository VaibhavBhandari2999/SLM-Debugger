from pathlib import Path

import jinja2

from django.conf import settings
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from .base import BaseEngine


class Jinja2(BaseEngine):

    app_dirname = 'jinja2'

    def __init__(self, params):
        """
        Initializes a Jinja2 environment for rendering templates.
        
        Args:
        params (dict): A dictionary containing configuration parameters for the Jinja2 environment.
        
        This method initializes a Jinja2 environment with the provided parameters. It populates the environment with context processors, sets up the environment class, and configures various options such as the loader, autoescape, and undefined behavior. The method also ensures that the environment is properly configured based on the settings and the provided parameters.
        
        Returns:
        None: This
        """

        params = params.copy()
        options = params.pop('OPTIONS').copy()
        super().__init__(params)

        self.context_processors = options.pop('context_processors', [])

        environment = options.pop('environment', 'jinja2.Environment')
        environment_cls = import_string(environment)

        if 'loader' not in options:
            options['loader'] = jinja2.FileSystemLoader(self.template_dirs)
        options.setdefault('autoescape', True)
        options.setdefault('auto_reload', settings.DEBUG)
        options.setdefault('undefined',
                           jinja2.DebugUndefined if settings.DEBUG else jinja2.Undefined)

        self.env = environment_cls(**options)

    def from_string(self, template_code):
        return Template(self.env.from_string(template_code), self)

    def get_template(self, template_name):
        """
        Retrieve a Jinja2 template by name.
        
        This method attempts to fetch a template from the environment and returns a Template object. If the template is not found, it raises a TemplateDoesNotExist exception. If there is a syntax error in the template, it catches the TemplateSyntaxError, wraps it in a new TemplateSyntaxError, and includes debug information before re-raising it.
        
        Parameters:
        template_name (str): The name of the template to retrieve.
        
        Returns:
        Template: A Jinja
        """

        try:
            return Template(self.env.get_template(template_name), self)
        except jinja2.TemplateNotFound as exc:
            raise TemplateDoesNotExist(exc.name, backend=self) from exc
        except jinja2.TemplateSyntaxError as exc:
            new = TemplateSyntaxError(exc.args)
            new.template_debug = get_exception_info(exc)
            raise new from exc

    @cached_property
    def template_context_processors(self):
        return [import_string(path) for path in self.context_processors]


class Template:

    def __init__(self, template, backend):
        self.template = template
        self.backend = backend
        self.origin = Origin(
            name=template.filename, template_name=template.name,
        )

    def render(self, context=None, request=None):
        from .utils import csrf_input_lazy, csrf_token_lazy
        if context is None:
            context = {}
        if request is not None:
            context['request'] = request
            context['csrf_input'] = csrf_input_lazy(request)
            context['csrf_token'] = csrf_token_lazy(request)
            for context_processor in self.backend.template_context_processors:
                context.update(context_processor(request))
        try:
            return self.template.render(context)
        except jinja2.TemplateSyntaxError as exc:
            new = TemplateSyntaxError(exc.args)
            new.template_debug = get_exception_info(exc)
            raise new from exc


class Origin:
    """
    A container to hold debug information as described in the template API
    documentation.
    """
    def __init__(self, name, template_name):
        self.name = name
        self.template_name = template_name


def get_exception_info(exception):
    """
    Format exception information for display on the debug page using the
    structure described in the template API documentation.
    """
    context_lines = 10
    lineno = exception.lineno
    source = exception.source
    if source is None:
        exception_file = Path(exception.filename)
        if exception_file.exists():
            with open(exception_file, 'r') as fp:
                source = fp.read()
    if source is not None:
        lines = list(enumerate(source.strip().split('\n'), start=1))
        during = lines[lineno - 1][1]
        total = len(lines)
        top = max(0, lineno - context_lines - 1)
        bottom = min(total, lineno + context_lines)
    else:
        during = ''
        lines = []
        total = top = bottom = 0
    return {
        'name': exception.filename,
        'message': exception.message,
        'source_lines': lines[top:bottom],
        'line': lineno,
        'before': '',
        'during': during,
        'after': '',
        'total': total,
        'top': top,
        'bottom': bottom,
    }
