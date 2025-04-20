import inspect

from . import _api


class Substitution:
    """
    A decorator that performs %-substitution on an object's docstring.

    This decorator should be robust even if ``obj.__doc__`` is None (for
    example, if -OO was passed to the interpreter).

    Usage: construct a docstring.Substitution with a sequence or dictionary
    suitable for performing substitution; then decorate a suitable function
    with the constructed object, e.g.::

        sub_author_name = Substitution(author='Jason')

        @sub_author_name
        def some_function(x):
            "%(author)s wrote this function"

        # note that some_function.__doc__ is now "Jason wrote this function"

    One can also use positional arguments::

        sub_first_last_names = Substitution('Edgar Allen', 'Poe')

        @sub_first_last_names
        def some_function(x):
            "%s %s wrote the Raven"
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize an instance of the class.
        
        This method is used to initialize an instance of the class with either positional arguments or keyword arguments, but not both.
        
        Parameters:
        *args: Positional arguments to initialize the instance.
        **kwargs: Keyword arguments to initialize the instance.
        
        Raises:
        TypeError: If both positional and keyword arguments are provided.
        
        Attributes:
        params: A tuple containing either the positional or keyword arguments provided during initialization.
        """

        if args and kwargs:
            raise TypeError("Only positional or keyword args are allowed")
        self.params = args or kwargs

    def __call__(self, func):
        """
        Decorates a function to format its docstring with provided parameters.
        
        Args:
        func (callable): The function to be decorated.
        
        Returns:
        callable: The decorated function with updated docstring.
        
        This decorator is used to enhance a function's docstring by replacing placeholders with actual parameter values. The docstring should contain placeholders enclosed in '%s' for parameters and '%(param_name)s' for keyword arguments. The decorator will update the docstring in place.
        
        Example:
        @docstring_formatter
        """

        if func.__doc__:
            func.__doc__ = inspect.cleandoc(func.__doc__) % self.params
        return func

    def update(self, *args, **kwargs):
        """
        Update ``self.params`` (which must be a dict) with the supplied args.
        """
        self.params.update(*args, **kwargs)


class _ArtistKwdocLoader(dict):
    def __missing__(self, key):
        if not key.endswith(":kwdoc"):
            raise KeyError(key)
        name = key[:-len(":kwdoc")]
        from matplotlib.artist import Artist, kwdoc
        try:
            cls, = [cls for cls in _api.recursive_subclasses(Artist)
                    if cls.__name__ == name]
        except ValueError as e:
            raise KeyError(key) from e
        return self.setdefault(key, kwdoc(cls))


class _ArtistPropertiesSubstitution(Substitution):
    """
    A `.Substitution` with two additional features:

    - Substitutions of the form ``%(classname:kwdoc)s`` (ending with the
      literal ":kwdoc" suffix) trigger lookup of an Artist subclass with the
      given *classname*, and are substituted with the `.kwdoc` of that class.
    - Decorating a class triggers substitution both on the class docstring and
      on the class' ``__init__`` docstring (which is a commonly required
      pattern for Artist subclasses).
    """

    def __init__(self):
        self.params = _ArtistKwdocLoader()

    def __call__(self, obj):
        super().__call__(obj)
        if isinstance(obj, type) and obj.__init__ != object.__init__:
            self(obj.__init__)
        return obj


def copy(source):
    """Copy a docstring from another source function (if present)."""
    def do_copy(target):
        if source.__doc__:
            target.__doc__ = source.__doc__
        return target
    return do_copy


# Create a decorator that will house the various docstring snippets reused
# throughout Matplotlib.
dedent_interpd = interpd = _ArtistPropertiesSubstitution()
