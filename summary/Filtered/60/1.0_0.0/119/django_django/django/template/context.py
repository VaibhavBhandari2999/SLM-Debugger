from contextlib import contextmanager
from copy import copy

# Hard-coded processor for easier use of CSRF protection.
_builtin_context_processors = ("django.template.context_processors.csrf",)


class ContextPopException(Exception):
    "pop() has been called more times than push()"
    pass


class ContextDict(dict):
    def __init__(self, context, *args, **kwargs):
        super().__init__(*args, **kwargs)

        context.dicts.append(self)
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.context.pop()


class BaseContext:
    def __init__(self, dict_=None):
        self._reset_dicts(dict_)

    def _reset_dicts(self, value=None):
        builtins = {"True": True, "False": False, "None": None}
        self.dicts = [builtins]
        if value is not None:
            self.dicts.append(value)

    def __copy__(self):
        duplicate = copy(super())
        duplicate.dicts = self.dicts[:]
        return duplicate

    def __repr__(self):
        return repr(self.dicts)

    def __iter__(self):
        return reversed(self.dicts)

    def push(self, *args, **kwargs):
        """
        Pushes multiple context dictionaries onto the current context stack.
        
        This method accepts a variable number of arguments, which can be either individual dictionaries or instances of the BaseContext class. Each BaseContext instance is expected to contain a list of dictionaries under the attribute `dicts`. These dictionaries are extracted and added to the argument list. The method then returns a new ContextDict object, which is a combination of the provided dictionaries and any keyword arguments.
        
        Parameters:
        *args: A variable number of arguments. Each
        """

        dicts = []
        for d in args:
            if isinstance(d, BaseContext):
                dicts += d.dicts[1:]
            else:
                dicts.append(d)
        return ContextDict(self, *dicts, **kwargs)

    def pop(self):
        if len(self.dicts) == 1:
            raise ContextPopException
        return self.dicts.pop()

    def __setitem__(self, key, value):
        "Set a variable in the current context"
        self.dicts[-1][key] = value

    def set_upward(self, key, value):
        """
        Set a variable in one of the higher contexts if it exists there,
        otherwise in the current context.
        """
        context = self.dicts[-1]
        for d in reversed(self.dicts):
            if key in d:
                context = d
                break
        context[key] = value

    def __getitem__(self, key):
        "Get a variable's value, starting at the current context and going upward"
        for d in reversed(self.dicts):
            if key in d:
                return d[key]
        raise KeyError(key)

    def __delitem__(self, key):
        "Delete a variable from the current context"
        del self.dicts[-1][key]

    def __contains__(self, key):
        return any(key in d for d in self.dicts)

    def get(self, key, otherwise=None):
        for d in reversed(self.dicts):
            if key in d:
                return d[key]
        return otherwise

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default

    def new(self, values=None):
        """
        Return a new context with the same properties, but with only the
        values given in 'values' stored.
        """
        new_context = copy(self)
        new_context._reset_dicts(values)
        return new_context

    def flatten(self):
        """
        Return self.dicts as one dictionary.
        """
        flat = {}
        for d in self.dicts:
            flat.update(d)
        return flat

    def __eq__(self, other):
        """
        Compare two contexts by comparing theirs 'dicts' attributes.
        """
        if not isinstance(other, BaseContext):
            return NotImplemented
        # flatten dictionaries because they can be put in a different order.
        return self.flatten() == other.flatten()


class Context(BaseContext):
    "A stack container for variable context"

    def __init__(self, dict_=None, autoescape=True, use_l10n=None, use_tz=None):
        """
        Initialize a new instance of the class.
        
        This method sets up the initial state of the object with the provided parameters.
        
        Parameters:
        dict_ (dict, optional): A dictionary to initialize the object with. Defaults to None.
        autoescape (bool, optional): A boolean indicating whether autoescaping is enabled. Defaults to True.
        use_l10n (bool, optional): A boolean indicating whether to use localization for date and number formatting. Defaults to None.
        use_tz (bool
        """

        self.autoescape = autoescape
        self.use_l10n = use_l10n
        self.use_tz = use_tz
        self.template_name = "unknown"
        self.render_context = RenderContext()
        # Set to the original template -- as opposed to extended or included
        # templates -- during rendering, see bind_template.
        self.template = None
        super().__init__(dict_)

    @contextmanager
    def bind_template(self, template):
        if self.template is not None:
            raise RuntimeError("Context is already bound to a template")
        self.template = template
        try:
            yield
        finally:
            self.template = None

    def __copy__(self):
        duplicate = super().__copy__()
        duplicate.render_context = copy(self.render_context)
        return duplicate

    def update(self, other_dict):
        "Push other_dict to the stack of dictionaries in the Context"
        if not hasattr(other_dict, "__getitem__"):
            raise TypeError("other_dict must be a mapping (dictionary-like) object.")
        if isinstance(other_dict, BaseContext):
            other_dict = other_dict.dicts[1:].pop()
        return ContextDict(self, other_dict)


class RenderContext(BaseContext):
    """
    A stack container for storing Template state.

    RenderContext simplifies the implementation of template Nodes by providing a
    safe place to store state between invocations of a node's `render` method.

    The RenderContext also provides scoping rules that are more sensible for
    'template local' variables. The render context stack is pushed before each
    template is rendered, creating a fresh scope with nothing in it. Name
    resolution fails if a variable is not found at the top of the RequestContext
    stack. Thus, variables are local to a specific template and don't affect the
    rendering of other templates as they would if they were stored in the normal
    template context.
    """

    template = None

    def __iter__(self):
        yield from self.dicts[-1]

    def __contains__(self, key):
        return key in self.dicts[-1]

    def get(self, key, otherwise=None):
        return self.dicts[-1].get(key, otherwise)

    def __getitem__(self, key):
        return self.dicts[-1][key]

    @contextmanager
    def push_state(self, template, isolated_context=True):
        """
        Push a new state onto the template stack.
        
        This function temporarily changes the current template to a new one and optionally creates an isolated context for the new template. The original template is restored after the operation.
        
        Parameters:
        template (str): The new template to use.
        isolated_context (bool, optional): If True, an isolated context is created for the new template. Defaults to True.
        
        Yields:
        None: This function is a generator and yields control back to the caller.
        
        Returns:
        """

        initial = self.template
        self.template = template
        if isolated_context:
            self.push()
        try:
            yield
        finally:
            self.template = initial
            if isolated_context:
                self.pop()


class RequestContext(Context):
    """
    This subclass of template.Context automatically populates itself using
    the processors defined in the engine's configuration.
    Additional processors can be specified as a list of callables
    using the "processors" keyword argument.
    """

    def __init__(
        self,
        request,
        dict_=None,
        processors=None,
        use_l10n=None,
        use_tz=None,
        autoescape=True,
    ):
        super().__init__(dict_, use_l10n=use_l10n, use_tz=use_tz, autoescape=autoescape)
        self.request = request
        self._processors = () if processors is None else tuple(processors)
        self._processors_index = len(self.dicts)

        # placeholder for context processors output
        self.update({})

        # empty dict for any new modifications
        # (so that context processors don't overwrite them)
        self.update({})

    @contextmanager
    def bind_template(self, template):
        if self.template is not None:
            raise RuntimeError("Context is already bound to a template")

        self.template = template
        # Set context processors according to the template engine's settings.
        processors = template.engine.template_context_processors + self._processors
        updates = {}
        for processor in processors:
            context = processor(self.request)
            try:
                updates.update(context)
            except TypeError as e:
                raise TypeError(
                    f"Context processor {processor.__qualname__} didn't return a "
                    "dictionary."
                ) from e

        self.dicts[self._processors_index] = updates

        try:
            yield
        finally:
            self.template = None
            # Unset context processors.
            self.dicts[self._processors_index] = {}

    def new(self, values=None):
        """
        Creates a new context for the request.
        
        This method initializes a new context using the superclass's `new` method and then removes any reference to context processors to maintain backwards compatibility. The method accepts an optional `values` parameter, which is used to initialize the context. The output is a new context object with the specified values and without the `_processors_index` attribute.
        
        Parameters:
        values (dict, optional): Initial values to be set in the context.
        
        Returns:
        object: A new context object
        """

        new_context = super().new(values)
        # This is for backwards-compatibility: RequestContexts created via
        # Context.new don't include values from context processors.
        if hasattr(new_context, "_processors_index"):
            del new_context._processors_index
        return new_context


def make_context(context, request=None, **kwargs):
    """
    Create a suitable Context from a plain dict and optionally an HttpRequest.
    """
    if context is not None and not isinstance(context, dict):
        raise TypeError(
            "context must be a dict rather than %s." % context.__class__.__name__
        )
    if request is None:
        context = Context(context, **kwargs)
    else:
        # The following pattern is required to ensure values from
        # context override those from template context processors.
        original_context = context
        context = RequestContext(request, **kwargs)
        if original_context:
            context.push(original_context)
    return context
