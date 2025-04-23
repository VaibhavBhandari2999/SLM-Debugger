from django.template import Library, Node

register = Library()


class CountRenderNode(Node):
    count = 0

    def render(self, context):
        """
        Render the template context.
        
        This method increments the count attribute, iterates over the flattened context values, and renders each value if it has a render method. If a value does not have a render method, it is ignored. The method returns a string representation of the count.
        
        Parameters:
        context (dict): The context dictionary containing the template variables.
        
        Returns:
        str: The string representation of the count attribute.
        """

        self.count += 1
        for v in context.flatten().values():
            try:
                v.render()
            except AttributeError:
                pass
        return str(self.count)


@register.tag
def count_render(parser, token):
    return CountRenderNode()
