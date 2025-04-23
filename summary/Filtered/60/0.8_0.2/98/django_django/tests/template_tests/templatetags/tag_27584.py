from django import template

register = template.Library()


@register.tag
def badtag(parser, token):
    """
    Parse a block of text until the 'endbadtag' token is encountered. This function is designed to handle a specific type of template tag in a parser. It removes the initial 'badtag' token and continues parsing until 'endbadtag' is found, at which point it stops and returns a 'BadNode' object.
    
    Parameters:
    parser (Parser): The parser object that is used to parse the template.
    token (Token): The token representing the start of the 'badtag
    """

    parser.parse(("endbadtag",))
    parser.delete_first_token()
    return BadNode()


class BadNode(template.Node):
    def render(self, context):
        raise template.TemplateSyntaxError("error")
