from django.template import Library, Node, TemplateSyntaxError
from django.utils import formats

register = Library()


@register.filter(is_safe=False)
def localize(value):
    """
    Force a value to be rendered as a localized value,
    regardless of the value of ``settings.USE_L10N``.
    """
    return str(formats.localize(value, use_l10n=True))


@register.filter(is_safe=False)
def unlocalize(value):
    """
    Force a value to be rendered as a non-localized value,
    regardless of the value of ``settings.USE_L10N``.
    """
    return str(formats.localize(value, use_l10n=False))


class LocalizeNode(Node):
    def __init__(self, nodelist, use_l10n):
        self.nodelist = nodelist
        self.use_l10n = use_l10n

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def render(self, context):
        """
        Render a template node list with modified localization settings.
        
        This function temporarily changes the `use_l10n` setting in the given context to the value of `self.use_l10n` before rendering the node list. After rendering, it restores the original `use_l10n` setting.
        
        Parameters:
        context (Context): The context in which the template is rendered.
        
        Returns:
        str: The rendered output of the template node list.
        
        Key Parameters:
        - `context`: The
        """

        old_setting = context.use_l10n
        context.use_l10n = self.use_l10n
        output = self.nodelist.render(context)
        context.use_l10n = old_setting
        return output


@register.tag('localize')
def localize_tag(parser, token):
    """
    Force or prevents localization of values, regardless of the value of
    `settings.USE_L10N`.

    Sample usage::

        {% localize off %}
            var pi = {{ 3.1415 }};
        {% endlocalize %}
    """
    use_l10n = None
    bits = list(token.split_contents())
    if len(bits) == 1:
        use_l10n = True
    elif len(bits) > 2 or bits[1] not in ('on', 'off'):
        raise TemplateSyntaxError("%r argument should be 'on' or 'off'" % bits[0])
    else:
        use_l10n = bits[1] == 'on'
    nodelist = parser.parse(('endlocalize',))
    parser.delete_first_token()
    return LocalizeNode(nodelist, use_l10n)
