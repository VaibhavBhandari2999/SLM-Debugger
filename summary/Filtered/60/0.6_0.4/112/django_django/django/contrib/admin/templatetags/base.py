from inspect import getfullargspec

from django.template.library import InclusionNode, parse_bits


class InclusionAdminNode(InclusionNode):
    """
    Template tag that allows its template to be overridden per model, per app,
    or globally.
    """

    def __init__(self, parser, token, func, template_name, takes_context=True):
        """
        This function initializes a custom template tag with the provided parser, token, function, template name, and optional context parameter.
        
        Parameters:
        parser (Parser): The template parser object.
        token (Token): The token object representing the tag.
        func (function): The function to be used as the custom template tag.
        template_name (str): The name of the template file associated with the tag.
        takes_context (bool, optional): Indicates whether the function takes the context as its first argument
        """

        self.template_name = template_name
        params, varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(
            func
        )
        bits = token.split_contents()
        args, kwargs = parse_bits(
            parser,
            bits[1:],
            params,
            varargs,
            varkw,
            defaults,
            kwonly,
            kwonly_defaults,
            takes_context,
            bits[0],
        )
        super().__init__(func, takes_context, args, kwargs, filename=None)

    def render(self, context):
        opts = context["opts"]
        app_label = opts.app_label.lower()
        object_name = opts.object_name.lower()
        # Load template for this render call. (Setting self.filename isn't
        # thread-safe.)
        context.render_context[self] = context.template.engine.select_template(
            [
                "admin/%s/%s/%s" % (app_label, object_name, self.template_name),
                "admin/%s/%s" % (app_label, self.template_name),
                "admin/%s" % self.template_name,
            ]
        )
        return super().render(context)
