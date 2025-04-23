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
        token (str): The token representing the tag.
        func (function): The function to be called when the tag is used.
        template_name (str): The name of the template file associated with the tag.
        takes_context (bool, optional): Whether the function takes a context argument. Defaults to True.
        
        This method initializes a custom template tag with the provided function, template name, and parameters.
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
        """
        Render the admin interface template for a specific model object.
        
        This method is responsible for rendering the template for a model object in the Django admin interface. It takes a context dictionary as input, which contains information about the model and the current request. The method first extracts the app label and object name from the context. It then selects the appropriate template for rendering the object based on the app label and object name. If a specific template for the object is not found, it falls back to a more general template
        """

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
