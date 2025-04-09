from urllib.parse import quote, urljoin

from django import template
from django.apps import apps
from django.utils.encoding import iri_to_uri
from django.utils.html import conditional_escape

register = template.Library()


class PrefixNode(template.Node):

    def __repr__(self):
        return "<PrefixNode for %r>" % self.name

    def __init__(self, varname=None, name=None):
        """
        Initialize a PrefixNode object.
        
        Args:
        varname (str): The variable name to store the result in.
        name (str): The name of the prefix node.
        
        Raises:
        TemplateSyntaxError: If no name is provided for the prefix node.
        
        Returns:
        None
        
        Summary:
        This method initializes a PrefixNode object with the given `varname` and `name`. If no `name` is provided, it raises a TemplateSyntaxError. The `var
        """

        if name is None:
            raise template.TemplateSyntaxError(
                "Prefix nodes must be given a name to return.")
        self.varname = varname
        self.name = name

    @classmethod
    def handle_token(cls, parser, token, name):
        """
        Class method to parse prefix node and return a Node.
        """
        # token.split_contents() isn't useful here because tags using this method don't accept variable as arguments
        tokens = token.contents.split()
        if len(tokens) > 1 and tokens[1] != 'as':
            raise template.TemplateSyntaxError(
                "First argument in '%s' must be 'as'" % tokens[0])
        if len(tokens) > 1:
            varname = tokens[2]
        else:
            varname = None
        return cls(varname, name)

    @classmethod
    def handle_simple(cls, name):
        """
        Generate a URI prefix based on the given setting name.
        
        Args:
        name (str): The name of the Django setting to retrieve the value from.
        
        Returns:
        str: The URI prefix derived from the setting value or an empty string if the setting is not found or Django is not installed.
        
        Raises:
        ImportError: If Django is not installed.
        
        Notes:
        - Uses `iri_to_uri` to convert the setting value to a URI.
        - Falls back to an empty
        """

        try:
            from django.conf import settings
        except ImportError:
            prefix = ''
        else:
            prefix = iri_to_uri(getattr(settings, name, ''))
        return prefix

    def render(self, context):
        """
        Render the template with the given context.
        
        Args:
        context (dict): The context dictionary containing the variables to be used in the template.
        
        Returns:
        str: The rendered template string.
        
        Summary:
        This function takes a context dictionary and renders the template with the given context. It first handles the simple name of the template using the `handle_simple` method. If a variable name is specified, it adds the rendered prefix to the context dictionary under the specified variable name. Finally,
        """

        prefix = self.handle_simple(self.name)
        if self.varname is None:
            return prefix
        context[self.varname] = prefix
        return ''


@register.tag
def get_static_prefix(parser, token):
    """
    Populate a template variable with the static prefix,
    ``settings.STATIC_URL``.

    Usage::

        {% get_static_prefix [as varname] %}

    Examples::

        {% get_static_prefix %}
        {% get_static_prefix as static_prefix %}
    """
    return PrefixNode.handle_token(parser, token, "STATIC_URL")


@register.tag
def get_media_prefix(parser, token):
    """
    Populate a template variable with the media prefix,
    ``settings.MEDIA_URL``.

    Usage::

        {% get_media_prefix [as varname] %}

    Examples::

        {% get_media_prefix %}
        {% get_media_prefix as media_prefix %}
    """
    return PrefixNode.handle_token(parser, token, "MEDIA_URL")


class StaticNode(template.Node):
    def __init__(self, varname=None, path=None):
        """
        Initialize a StaticNode with the given path and optional varname.
        
        Args:
        path (str): The path to the static file to be returned.
        varname (str, optional): The name of the variable to store the result in. Defaults to None.
        
        Raises:
        TemplateSyntaxError: If no path is provided.
        
        Returns:
        None: This method does not return anything, but initializes the node with the given path and optional varname.
        """

        if path is None:
            raise template.TemplateSyntaxError(
                "Static template nodes must be given a path to return.")
        self.path = path
        self.varname = varname

    def url(self, context):
        path = self.path.resolve(context)
        return self.handle_simple(path)

    def render(self, context):
        """
        Renders a URL based on the given context and stores it in a variable if specified.
        
        Args:
        context (Context): The context containing the necessary information to generate the URL.
        
        Returns:
        str: The rendered URL or an empty string if no variable name is specified.
        
        Summary:
        This function takes a context object, generates a URL using the `url` method, and optionally stores it in a variable. If `autoescape` is enabled in the context, the URL is
        """

        url = self.url(context)
        if context.autoescape:
            url = conditional_escape(url)
        if self.varname is None:
            return url
        context[self.varname] = url
        return ''

    @classmethod
    def handle_simple(cls, path):
        """
        Generate a URL for a given path.
        
        This function handles the generation of a URL for a given path, taking into account whether 'django.contrib.staticfiles' is installed. If it is, it uses `staticfiles_storage.url` to generate the URL. Otherwise, it constructs the URL by joining the "STATIC_URL" prefix with the quoted path using `urljoin`.
        
        Args:
        path (str): The path for which to generate the URL.
        
        Returns:
        str: The generated
        """

        if apps.is_installed('django.contrib.staticfiles'):
            from django.contrib.staticfiles.storage import staticfiles_storage
            return staticfiles_storage.url(path)
        else:
            return urljoin(PrefixNode.handle_simple("STATIC_URL"), quote(path))

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse prefix node and return a Node.
        """
        bits = token.split_contents()

        if len(bits) < 2:
            raise template.TemplateSyntaxError(
                "'%s' takes at least one argument (path to file)" % bits[0])

        path = parser.compile_filter(bits[1])

        if len(bits) >= 2 and bits[-2] == 'as':
            varname = bits[3]
        else:
            varname = None

        return cls(varname, path)


@register.tag('static')
def do_static(parser, token):
    """
    Join the given path with the STATIC_URL setting.

    Usage::

        {% static path [as varname] %}

    Examples::

        {% static "myapp/css/base.css" %}
        {% static variable_with_path %}
        {% static "myapp/css/base.css" as admin_base_css %}
        {% static variable_with_path as varname %}
    """
    return StaticNode.handle_token(parser, token)


def static(path):
    """
    Given a relative path to a static asset, return the absolute path to the
    asset.
    """
    return StaticNode.handle_simple(path)
