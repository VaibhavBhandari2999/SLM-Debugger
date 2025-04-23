import os
import platform
import sys
import traceback
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..outcomes import fail
from ..outcomes import TEST_OUTCOME
from .structures import Mark
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.store import StoreKey


evalcache_key = StoreKey[Dict[str, Any]]()


def cached_eval(config: Config, expr: str, d: Dict[str, object]) -> Any:
    """
    Evaluate an expression in the context of a given dictionary.
    
    This function evaluates a string expression in the context of a provided dictionary `d`. It uses a cache to store previously evaluated expressions to improve performance. The cache is stored in the `evalcache` attribute of the `config` object under a specific key.
    
    Parameters:
    config (Config): The configuration object containing the cache.
    expr (str): The expression to evaluate.
    d (Dict[str, object]): The dictionary providing the context for
    """

    default = {}  # type: Dict[str, object]
    evalcache = config._store.setdefault(evalcache_key, default)
    try:
        return evalcache[expr]
    except KeyError:
        import _pytest._code

        exprcode = _pytest._code.compile(expr, mode="eval")
        evalcache[expr] = x = eval(exprcode, d)
        return x


class MarkEvaluator:
    def __init__(self, item: Item, name: str) -> None:
        self.item = item
        self._marks = None  # type: Optional[List[Mark]]
        self._mark = None  # type: Optional[Mark]
        self._mark_name = name

    def __bool__(self) -> bool:
        # don't cache here to prevent staleness
        return bool(self._get_marks())

    def wasvalid(self) -> bool:
        return not hasattr(self, "exc")

    def _get_marks(self) -> List[Mark]:
        return list(self.item.iter_markers(name=self._mark_name))

    def invalidraise(self, exc) -> Optional[bool]:
        raises = self.get("raises")
        if not raises:
            return None
        return not isinstance(exc, raises)

    def istrue(self) -> bool:
        try:
            return self._istrue()
        except TEST_OUTCOME:
            self.exc = sys.exc_info()
            if isinstance(self.exc[1], SyntaxError):
                # TODO: Investigate why SyntaxError.offset is Optional, and if it can be None here.
                assert self.exc[1].offset is not None
                msg = [" " * (self.exc[1].offset + 4) + "^"]
                msg.append("SyntaxError: invalid syntax")
            else:
                msg = traceback.format_exception_only(*self.exc[:2])
            fail(
                "Error evaluating %r expression\n"
                "    %s\n"
                "%s" % (self._mark_name, self.expr, "\n".join(msg)),
                pytrace=False,
            )

    def _getglobals(self) -> Dict[str, object]:
        """
        Retrieve the global namespace for the current item.
        
        This method returns a dictionary containing the global namespace for the current item. The dictionary includes the following keys:
        - 'os': The os module.
        - 'sys': The sys module.
        - 'platform': The platform module.
        - 'config': The configuration object associated with the current item.
        
        If the current item has an attribute 'obj', the global namespace of 'obj' is also included in the dictionary.
        
        Returns:
        Dict[str, object]: A
        """

        d = {"os": os, "sys": sys, "platform": platform, "config": self.item.config}
        if hasattr(self.item, "obj"):
            d.update(self.item.obj.__globals__)  # type: ignore[attr-defined] # noqa: F821
        return d

    def _istrue(self) -> bool:
        if hasattr(self, "result"):
            result = getattr(self, "result")  # type: bool
            return result
        self._marks = self._get_marks()

        if self._marks:
            self.result = False
            for mark in self._marks:
                self._mark = mark
                if "condition" not in mark.kwargs:
                    args = mark.args
                else:
                    args = (mark.kwargs["condition"],)

                for expr in args:
                    self.expr = expr
                    if isinstance(expr, str):
                        d = self._getglobals()
                        result = cached_eval(self.item.config, expr, d)
                    else:
                        if "reason" not in mark.kwargs:
                            # XXX better be checked at collection time
                            msg = (
                                "you need to specify reason=STRING "
                                "when using booleans as conditions."
                            )
                            fail(msg)
                        result = bool(expr)
                    if result:
                        self.result = True
                        self.reason = mark.kwargs.get("reason", None)
                        self.expr = expr
                        return self.result

                if not args:
                    self.result = True
                    self.reason = mark.kwargs.get("reason", None)
                    return self.result
        return False

    def get(self, attr, default=None):
        if self._mark is None:
            return default
        return self._mark.kwargs.get(attr, default)

    def getexplanation(self):
        expl = getattr(self, "reason", None) or self.get("reason", None)
        if not expl:
            if not hasattr(self, "expr"):
                return ""
            else:
                return "condition: " + str(self.expr)
        return expl
