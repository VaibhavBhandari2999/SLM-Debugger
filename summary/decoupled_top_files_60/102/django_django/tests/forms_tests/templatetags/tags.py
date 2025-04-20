from django.template import Library, Node

register = Library()


class CountRenderNode(Node):
    count = 0

    def render(self, context):
        """
        Renders the template and increments a count for each context.
        
        Parameters:
        context (dict): The context dictionary containing variables and their values.
        
        Returns:
        str: The current count as a string after rendering the context.
        
        This function increments the count attribute of the object and iterates over all values in the context. It attempts to render each value if it has a render method. If a value does not have a render method, it is ignored. The function finally returns the current count as a
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
