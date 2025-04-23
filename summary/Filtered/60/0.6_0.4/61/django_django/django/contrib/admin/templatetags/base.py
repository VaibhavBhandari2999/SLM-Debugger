from inspect import getfullargspec

from django.template.library import InclusionNode, parse_bits


class InclusionAdminNode(InclusionNode):
    """
    Template tag that allows its template to be overridden per model, per app,
    or globally.
    """

    def __init__(self, parser, token, func, template_name, takes_context=True):
        """
        Initialize a custom template tag.
        
        Args:
        parser (Parser): The template parser object.
        token (Token): The token object representing the tag.
        func (Callable): The function to be called when the tag is used.
        template_name (str): The name of the template file associated with the tag.
        takes_context (bool, optional): Indicates whether the function takes a context argument. Defaults to True.
        
        This method initializes a custom template tag with the provided function, template name, and
        """

        self.template_name = template_name
        params, varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(func)
        bits = token.split_contents()
        args, kwargs = parse_bits(
            parser, bits[1:], params, varargs, varkw, defaults, kwonly,
            kwonly_defaults, takes_context, bits[0],
        )
        super().__init__(func, takes_context, args, kwargs, filename=None)

    def render(self, context):
        """
        The `render` method is a custom rendering function for an admin interface in Django. It takes a context dictionary as input and processes it to render a template for displaying admin interface elements.
        
        ### Parameters:
        - `context`: A dictionary containing the context data for the template. This includes information such as the model options, app label, and object name.
        
        ### Key Steps:
        1. Extracts the app label and object name from the context.
        2. Selects a template to render based on the app
        """

        opts = context['opts']
        app_label = opts.app_label.lower()
        object_name = opts.object_name.lower()
        # Load template for this render call. (Setting self.filename isn't
        # thread-safe.)
        context.render_context[self] = context.template.engine.select_template([
            'admin/%s/%s/%s' % (app_label, object_name, self.template_name),
            'admin/%s/%s' % (app_label, self.template_name),
            'admin/%s' % self.template_name,
        ])
        return super().render(context)
