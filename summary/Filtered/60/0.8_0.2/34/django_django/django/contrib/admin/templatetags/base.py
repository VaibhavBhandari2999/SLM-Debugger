from inspect import getfullargspec

from django.template.library import InclusionNode, parse_bits


class InclusionAdminNode(InclusionNode):
    """
    Template tag that allows its template to be overridden per model, per app,
    or globally.
    """

    def __init__(self, parser, token, func, template_name, takes_context=True):
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
        The `render` method is responsible for rendering the admin interface template for a given model. It takes a context dictionary as input and returns the rendered template.
        
        Key Parameters:
        - `context`: A dictionary containing the context information required for rendering the template. This includes details like the model options, app label, and object name.
        
        Key Steps:
        1. Extracts the app label and object name from the context.
        2. Selects the appropriate template from a list of possible template paths.
        3. Renders
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
