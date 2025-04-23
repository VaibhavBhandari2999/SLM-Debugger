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
        
        This method sets up a PrefixNode object with a given name and an optional varname. If no name is provided, a TemplateSyntaxError is raised.
        
        Parameters:
        varname (str, optional): The variable name to store the result in.
        name (str): The name of the prefix node, which is required and will be returned.
        
        Raises:
        template.TemplateSyntaxError: If no name is provided.
        
        Returns:
        None: This method does not return
        """

        if name is None:
            raise template.TemplateSyntaxError(
                "Prefix nodes must be given a name to return."
            )
        self.varname = varname
        self.name = name

    @classmethod
    def handle_token(cls, parser, token, name):
        """
        Class method to parse prefix node and return a Node.
        """
        # token.split_contents() isn't useful here because tags using this
        # method don't accept variable as arguments.
        tokens = token.contents.split()
        if len(tokens) > 1 and tokens[1] != "as":
            raise template.TemplateSyntaxError(
                "First argument in '%s' must be 'as'" % tokens[0]
            )
        if len(tokens) > 1:
            varname = tokens[2]
        else:
            varname = None
        return cls(varname, name)

    @classmethod
    def handle_simple(cls, name):
        try:
            from django.conf import settings
        except ImportError:
            prefix = ""
        else:
            prefix = iri_to_uri(getattr(settings, name, ""))
        return prefix

    def render(self, context):
        """
        Renders the template tag and stores the result in the context with the specified variable name.
        
        Parameters:
        context (Context): The context in which the template tag is being rendered.
        
        Returns:
        str: The rendered prefix if no variable name is specified, otherwise returns an empty string.
        
        Key Parameters:
        - name (str): The name of the template tag.
        - varname (str, optional): The variable name to store the rendered prefix in the context.
        
        Usage:
        This function is
        """

        prefix = self.handle_simple(self.name)
        if self.varname is None:
            return prefix
        context[self.varname] = prefix
        return ""


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
    child_nodelists = ()

    def __init__(self, varname=None, path=None):
        """
        Initializes a StaticNode object.
        
        This method sets up a StaticNode object with a given path and an optional variable name.
        
        Parameters:
        varname (str, optional): The name of the variable to store the result. Defaults to None.
        path (str): The path to the static file to be served.
        
        Raises:
        template.TemplateSyntaxError: If no path is provided.
        
        Returns:
        None: This method does not return any value. It initializes the StaticNode object.
        """

        if path is None:
            raise template.TemplateSyntaxError(
                "Static template nodes must be given a path to return."
            )
        self.path = path
        self.varname = varname

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(varname={self.varname!r}, path={self.path!r})"
        )

    def url(self, context):
        path = self.path.resolve(context)
        return self.handle_simple(path)

    def render(self, context):
        url = self.url(context)
        if context.autoescape:
            url = conditional_escape(url)
        if self.varname is None:
            return url
        context[self.varname] = url
        return ""

    @classmethod
    def handle_simple(cls, path):
        """
        Generate a URL for a static file given a path.
        
        This function handles the generation of a URL for a static file using the provided path. It first checks if the "django.contrib.staticfiles" app is installed. If it is, it uses the staticfiles storage to get the URL. If not, it constructs the URL by joining the "STATIC_URL" prefix with the quoted path.
        
        Parameters:
        path (str): The path to the static file.
        
        Returns:
        str: The URL for
        """

        if apps.is_installed("django.contrib.staticfiles"):
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
                "'%s' takes at least one argument (path to file)" % bits[0]
            )

        path = parser.compile_filter(bits[1])

        if len(bits) >= 2 and bits[-2] == "as":
            varname = bits[3]
        else:
            varname = None

        return cls(varname, path)


@register.tag("static")
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
