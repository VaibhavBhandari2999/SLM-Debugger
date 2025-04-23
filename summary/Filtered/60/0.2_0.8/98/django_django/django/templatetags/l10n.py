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
        return "<%s>" % self.__class__.__name__

    def render(self, context):
        """
        Renders a Django template node list with localization settings temporarily adjusted.
        
        This function is designed to be used within a custom Django template tag or filter. It temporarily changes the `use_l10n` context variable to the value of `self.use_l10n` while rendering the node list, ensuring that the localization settings are applied as required. After rendering, the original `use_l10n` setting is restored.
        
        Parameters:
        context (Context): The Django template context in which the
        """

        old_setting = context.use_l10n
        context.use_l10n = self.use_l10n
        output = self.nodelist.render(context)
        context.use_l10n = old_setting
        return output


@register.tag("localize")
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
    elif len(bits) > 2 or bits[1] not in ("on", "off"):
        raise TemplateSyntaxError("%r argument should be 'on' or 'off'" % bits[0])
    else:
        use_l10n = bits[1] == "on"
    nodelist = parser.parse(("endlocalize",))
    parser.delete_first_token()
    return LocalizeNode(nodelist, use_l10n)
