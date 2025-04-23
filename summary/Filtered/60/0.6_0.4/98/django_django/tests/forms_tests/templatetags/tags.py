from django.template import Library, Node

register = Library()


class CountRenderNode(Node):
    count = 0

    def render(self, context):
        """
        Render a template context.
        
        This method increments a counter and renders each value in the flattened context. If a value does not have a 'render' method, it is skipped. The method returns the current count as a string.
        
        Parameters:
        context (dict): The context to render.
        
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
