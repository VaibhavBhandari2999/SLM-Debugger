import pprint
import reprlib
from typing import Any
from typing import Dict
from typing import IO
from typing import Optional


def _try_repr_or_str(obj: object) -> str:
    try:
        return repr(obj)
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        return '{}("{}")'.format(type(obj).__name__, obj)


def _format_repr_exception(exc: BaseException, obj: object) -> str:
    """
    Generate a formatted string representation of an exception raised during the repr() of an object.
    
    Args:
    exc (BaseException): The exception that was raised.
    obj (object): The object whose representation was being generated when the exception occurred.
    
    Returns:
    str: A formatted string indicating the exception and the object's type and identity.
    """

    try:
        exc_info = _try_repr_or_str(exc)
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as exc:
        exc_info = "unpresentable exception ({})".format(_try_repr_or_str(exc))
    return "<[{} raised in repr()] {} object at 0x{:x}>".format(
        exc_info, type(obj).__name__, id(obj)
    )


def _ellipsize(s: str, maxsize: int) -> str:
    if len(s) > maxsize:
        i = max(0, (maxsize - 3) // 2)
        j = max(0, maxsize - 3 - i)
        return s[:i] + "..." + s[len(s) - j :]
    return s


class SafeRepr(reprlib.Repr):
    """repr.Repr that limits the resulting size of repr() and includes
    information on exceptions raised during the call."""

    def __init__(self, maxsize: int) -> None:
        super().__init__()
        self.maxstring = maxsize
        self.maxsize = maxsize

    def repr(self, x: object) -> str:
        """
        Generate a string representation of an object.
        
        Args:
        x (object): The object to be represented.
        
        Returns:
        str: A string representation of the object, possibly truncated to avoid excessive length.
        """

        try:
            s = super().repr(x)
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as exc:
            s = _format_repr_exception(exc, x)
        return _ellipsize(s, self.maxsize)

    def repr_instance(self, x: object, level: int) -> str:
        try:
            s = repr(x)
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as exc:
            s = _format_repr_exception(exc, x)
        return _ellipsize(s, self.maxsize)


def safeformat(obj: object) -> str:
    """Return a pretty printed string for the given object.

    Failing __repr__ functions of user instances will be represented
    with a short exception info.
    """
    try:
        return pprint.pformat(obj)
    except Exception as exc:
        return _format_repr_exception(exc, obj)


def saferepr(obj: object, maxsize: int = 240) -> str:
    """Return a size-limited safe repr-string for the given object.

    Failing __repr__ functions of user instances will be represented
    with a short exception info and 'saferepr' generally takes
    care to never raise exceptions itself.

    This function is a wrapper around the Repr/reprlib functionality of the
    standard 2.6 lib.
    """
    return SafeRepr(maxsize).repr(obj)


class AlwaysDispatchingPrettyPrinter(pprint.PrettyPrinter):
    """PrettyPrinter that always dispatches (regardless of width)."""

    def _format(
        self,
        object: object,
        stream: IO[str],
        indent: int,
        allowance: int,
        context: Dict[int, Any],
        level: int,
    ) -> None:
        # Type ignored because _dispatch is private.
        p = self._dispatch.get(type(object).__repr__, None)  # type: ignore[attr-defined]

        objid = id(object)
        if objid in context or p is None:
            # Type ignored because _format is private.
            super()._format(  # type: ignore[misc]
                object,
                stream,
                indent,
                allowance,
                context,
                level,
            )
            return

        context[objid] = 1
        p(self, object, stream, indent, allowance, context, level + 1)
        del context[objid]


def _pformat_dispatch(
    object: object,
    indent: int = 1,
    width: int = 80,
    depth: Optional[int] = None,
    *,
    compact: bool = False,
) -> str:
    return AlwaysDispatchingPrettyPrinter(
        indent=indent, width=width, depth=depth, compact=compact
    ).pformat(object)
