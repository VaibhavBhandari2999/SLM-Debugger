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
        Initialize a new instance of the class.
        
        This method is used to create a new instance of the class. It accepts either positional arguments or keyword arguments, but not both. If both are provided, a TypeError is raised.
        
        Parameters:
        *args: Variable length argument list. Used to pass non-keyworded variable length arguments.
        **kwargs: Arbitrary keyword arguments. Used to pass keyworded, variable-length argument list.
        
        Raises:
        TypeError: If both *args and **kwargs are provided.
        """

        if args and kwargs:
            raise TypeError("Only positional or keyword args are allowed")
        self.params = args or kwargs

    def __call__(self, func):
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
        """
        Generate a docstring for the provided function.
        
        This function is designed to handle missing keys in a dictionary-like object. If the key does not end with ":kwdoc", it raises a KeyError. Otherwise, it extracts the base name of the key, looks up the corresponding class in the `Artist` subclass hierarchy, and returns the keyword documentation for that class.
        
        Parameters:
        key (str): The key for which the function is checking and generating documentation.
        
        Returns:
        str: The keyword documentation for
        """

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
