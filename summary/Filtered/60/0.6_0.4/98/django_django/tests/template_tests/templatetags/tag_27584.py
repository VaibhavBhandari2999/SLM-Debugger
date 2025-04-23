from django import template

register = template.Library()


@register.tag
def badtag(parser, token):
    """
    Parse a block of text until the 'endbadtag' token is encountered. The function removes the first token from the parser's token stream after parsing. It returns an instance of the BadNode class.
    
    Parameters:
    parser (Parser): The parser object that contains the token stream to be processed.
    token (str): The starting token that triggers the parsing block.
    
    Returns:
    BadNode: An instance of the BadNode class, representing the parsed content until 'endbadtag' is encountered
    """

    parser.parse(("endbadtag",))
    parser.delete_first_token()
    return BadNode()


class BadNode(template.Node):
    def render(self, context):
        raise template.TemplateSyntaxError("error")
