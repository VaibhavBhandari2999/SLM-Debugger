from django import template

register = template.Library()


@register.tag
def badtag(parser, token):
    """
    Parse a block of text until the 'endbadtag' token is encountered. The function removes the initial 'badtag' token and returns a BadNode object. This function is used in a template parser to handle a specific type of tag that needs to be parsed until its corresponding closing tag.
    
    Parameters:
    parser (Parser): The template parser instance that processes the tokens.
    token (Token): The current token being processed, which is expected to be 'badtag'.
    
    Returns:
    BadNode
    """

    parser.parse(("endbadtag",))
    parser.delete_first_token()
    return BadNode()


class BadNode(template.Node):
    def render(self, context):
        raise template.TemplateSyntaxError("error")
