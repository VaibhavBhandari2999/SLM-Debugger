from django import template

register = template.Library()


@register.tag
def badtag(parser, token):
    """
    Parse and ignore content between 'badtag' and 'endbadtag' tags.
    
    This function is used to define a custom template tag in a Django template. It takes a parser and a token as input and returns a BadNode object. The parser is used to parse the template content until the 'endbadtag' tag is encountered. The 'delete_first_token' method is called to remove the 'badtag' token from the parser's token stream.
    
    Parameters:
    parser (Parser): The
    """

    parser.parse(("endbadtag",))
    parser.delete_first_token()
    return BadNode()


class BadNode(template.Node):
    def render(self, context):
        raise template.TemplateSyntaxError("error")
