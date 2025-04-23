import functools
import inspect


@functools.lru_cache(maxsize=512)
def _get_func_parameters(func, remove_first):
    """
    Get the parameters of a function.
    
    Args:
    func (callable): The function to inspect.
    remove_first (bool): If True, the first parameter will be removed from the result.
    
    Returns:
    tuple: A tuple of Parameter objects representing the function's parameters, excluding the first parameter if specified.
    
    Example:
    >>> def example_func(a, b, c=3):
    ...     pass
    >>> _get_func_parameters(example_func, remove_first=True)
    (<Parameter("b")
    """

    parameters = tuple(inspect.signature(func).parameters.values())
    if remove_first:
        parameters = parameters[1:]
    return parameters


def _get_callable_parameters(meth_or_func):
    """
    Retrieve the parameters of a given method or function.
    
    This function extracts the parameters of a provided method or function. If the input is a method, it removes the 'self' parameter by default.
    
    Args:
    meth_or_func (function or method): The method or function to extract parameters from.
    
    Returns:
    list: A list of parameter names (strings) for the given method or function.
    """

    is_method = inspect.ismethod(meth_or_func)
    func = meth_or_func.__func__ if is_method else meth_or_func
    return _get_func_parameters(func, remove_first=is_method)


def get_func_args(func):
    """
    Retrieve the positional argument names of a function.
    
    Args:
    func (callable): The function to inspect.
    
    Returns:
    list: A list of positional argument names.
    
    Example:
    >>> def example_function(arg1, arg2, kwarg1=None, kwarg2='default'):
    ...     pass
    >>> get_func_args(example_function)
    ['arg1', 'arg2']
    """

    params = _get_callable_parameters(func)
    return [
        param.name for param in params
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    ]


def get_func_full_args(func):
    """
    Return a list of (argument name, default value) tuples. If the argument
    does not have a default value, omit it in the tuple. Arguments such as
    *args and **kwargs are also included.
    """
    params = _get_callable_parameters(func)
    args = []
    for param in params:
        name = param.name
        # Ignore 'self'
        if name == 'self':
            continue
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            name = '*' + name
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            name = '**' + name
        if param.default != inspect.Parameter.empty:
            args.append((name, param.default))
        else:
            args.append((name,))
    return args


def func_accepts_kwargs(func):
    """Return True if function 'func' accepts keyword arguments **kwargs."""
    return any(
        p for p in _get_callable_parameters(func)
        if p.kind == p.VAR_KEYWORD
    )


def func_accepts_var_args(func):
    """
    Return True if function 'func' accepts positional arguments *args.
    """
    return any(
        p for p in _get_callable_parameters(func)
        if p.kind == p.VAR_POSITIONAL
    )


def method_has_no_args(meth):
    """Return True if a method only accepts 'self'."""
    count = len([
        p for p in _get_callable_parameters(meth)
        if p.kind == p.POSITIONAL_OR_KEYWORD
    ])
    return count == 0 if inspect.ismethod(meth) else count == 1


def func_supports_parameter(func, name):
    return any(param.name == name for param in _get_callable_parameters(func))
