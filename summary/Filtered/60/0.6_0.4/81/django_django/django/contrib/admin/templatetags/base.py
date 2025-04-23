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
        The `render` method is a custom rendering function for an admin interface in Django. It is responsible for selecting and rendering a template based on the provided context.
        
        Parameters:
        - `context`: A dictionary-like object containing the context information for the template rendering. This includes details such as the model options (`opts`), the application label (`app_label`), and the object name (`object_name`).
        
        Key Steps:
        1. Extracts the application label and object name from the context.
        2. Select
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
