from django.template import Library, Node

register = Library()


class CountRenderNode(Node):
    count = 0

    def render(self, context):
        """
        Render a template context.
        
        This method increments a count for each call, then iterates through the flattened context values. For each value, it attempts to call the 'render' method. If the value does not have a 'render' method, it is ignored. The method returns the current count as a string.
        
        Parameters:
        context (dict): A dictionary representing the template context.
        
        Returns:
        str: The current count as a string.
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
