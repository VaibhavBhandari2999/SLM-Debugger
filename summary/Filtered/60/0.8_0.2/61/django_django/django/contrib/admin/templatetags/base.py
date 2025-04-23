from inspect import getfullargspec

from django.template.library import InclusionNode, parse_bits


class InclusionAdminNode(InclusionNode):
    """
    Template tag that allows its template to be overridden per model, per app,
    or globally.
    """

    def __init__(self, parser, token, func, template_name, takes_context=True):
        """
        The __init__ method initializes the function with the provided parser, token, and other parameters. It takes the following arguments:
        - parser: The template parser object.
        - token: The token object representing the tag.
        - func: The function to be called.
        - template_name: The name of the template.
        - takes_context (optional, default=True): A boolean indicating whether the function takes context as an argument.
        
        The method parses the token to extract arguments and keyword arguments, and then initializes the super
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
        The `render` method is a custom rendering function for an admin interface template. It takes a `context` object as input, which is expected to contain the necessary information for rendering the template. The method performs the following steps:
        
        1. Extracts the `opts` object from the `context`, which contains metadata about the model being rendered.
        2. Retrieves the `app_label` and `object_name` from the `opts` object, converting them to lowercase.
        3. Selects the appropriate
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
