import pprint
import reprlib
from typing import Any


def _try_repr_or_str(obj):
    """
    Generate a string representation of an object.
    
    This function attempts to use the `repr` function to get a string representation of the provided object. If `repr` raises an exception, it falls back to using `str` to convert the object to a string. This is useful for debugging or logging purposes where you want a string representation of an object that can handle exceptions gracefully.
    
    Parameters:
    obj (Any): The object to be represented as a string.
    
    Returns:
    str: A string representation of
    """

    try:
        return repr(obj)
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        return '{}("{}")'.format(type(obj).__name__, obj)


def _format_repr_exception(exc: BaseException, obj: Any) -> str:
    try:
        exc_info = _try_repr_or_str(exc)
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as exc:
        exc_info = "unpresentable exception ({})".format(_try_repr_or_str(exc))
    return "<[{} raised in repr()] {} object at 0x{:x}>".format(
        exc_info, obj.__class__.__name__, id(obj)
    )


def _ellipsize(s: str, maxsize: int) -> str:
    """
    Ellipsize a string to fit within a specified maximum size.
    
    Args:
    s (str): The input string to be ellipsized.
    maxsize (int): The maximum length of the string after ellipsizing.
    
    Returns:
    str: The ellipsized string.
    """

    if len(s) > maxsize:
        i = max(0, (maxsize - 3) // 2)
        j = max(0, maxsize - 3 - i)
        return s[:i] + "..." + s[len(s) - j :]
    return s


class SafeRepr(reprlib.Repr):
    """subclass of repr.Repr that limits the resulting size of repr()
    and includes information on exceptions raised during the call.
    """

    def __init__(self, maxsize: int) -> None:
        super().__init__()
        self.maxstring = maxsize
        self.maxsize = maxsize

    def repr(self, x: Any) -> str:
        try:
            s = super().repr(x)
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as exc:
            s = _format_repr_exception(exc, x)
        return _ellipsize(s, self.maxsize)

    def repr_instance(self, x: Any, level: int) -> str:
        """
        Generate a string representation of an instance with optional ellipsis.
        
        This function attempts to generate a string representation of the given instance `x`. If successful, it returns the string. If an exception is raised during the process, it catches the exception and returns a formatted error message instead. The output string is then ellipsized to a maximum length specified by `self.maxsize`.
        
        Parameters:
        x (Any): The instance to be represented as a string.
        level (int): The indentation level for
        """

        try:
            s = repr(x)
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as exc:
            s = _format_repr_exception(exc, x)
        return _ellipsize(s, self.maxsize)


def safeformat(obj: Any) -> str:
    """return a pretty printed string for the given object.
    Failing __repr__ functions of user instances will be represented
    with a short exception info.
    """
    try:
        return pprint.pformat(obj)
    except Exception as exc:
        return _format_repr_exception(exc, obj)


def saferepr(obj: Any, maxsize: int = 240) -> str:
    """return a size-limited safe repr-string for the given object.
    Failing __repr__ functions of user instances will be represented
    with a short exception info and 'saferepr' generally takes
    care to never raise exceptions itself.  This function is a wrapper
    around the Repr/reprlib functionality of the standard 2.6 lib.
    """
    return SafeRepr(maxsize).repr(obj)
