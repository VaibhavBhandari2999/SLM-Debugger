import os
import platform
import sys
import traceback

from ..outcomes import fail
from ..outcomes import TEST_OUTCOME


def cached_eval(config, expr, d):
    """
    Evaluate an expression in the context of a given dictionary.
    
    This function evaluates an expression in the context of a given dictionary.
    If the expression has been evaluated before, the cached result is returned.
    Otherwise, the expression is compiled and evaluated, and the result is stored
    for future use.
    
    Parameters:
    config (object): The configuration object that holds the cache.
    expr (str): The expression to be evaluated.
    d (dict): The dictionary containing the context in which the expression
    should
    """

    if not hasattr(config, "_evalcache"):
        config._evalcache = {}
    try:
        return config._evalcache[expr]
    except KeyError:
        import _pytest._code

        exprcode = _pytest._code.compile(expr, mode="eval")
        config._evalcache[expr] = x = eval(exprcode, d)
        return x


class MarkEvaluator:
    def __init__(self, item, name):
        self.item = item
        self._marks = None
        self._mark = None
        self._mark_name = name

    def __bool__(self):
        # don't cache here to prevent staleness
        return bool(self._get_marks())

    __nonzero__ = __bool__

    def wasvalid(self):
        return not hasattr(self, "exc")

    def _get_marks(self):
        return list(self.item.iter_markers(name=self._mark_name))

    def invalidraise(self, exc):
        raises = self.get("raises")
        if not raises:
            return
        return not isinstance(exc, raises)

    def istrue(self):
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

    def _getglobals(self):
        d = {"os": os, "sys": sys, "platform": platform, "config": self.item.config}
        if hasattr(self.item, "obj"):
            d.update(self.item.obj.__globals__)
        return d

    def _istrue(self):
        """
        Function to determine if a test condition is true.
        
        This function checks if a test condition is true based on the marks associated with the test. It evaluates the conditions provided in the marks and returns `True` if any of the conditions evaluate to `True`. Otherwise, it returns `False`.
        
        Parameters:
        None (the function uses attributes and methods of the instance it is called on)
        
        Returns:
        bool: `True` if any of the conditions evaluate to `True`, otherwise `False`.
        
        Attributes
        """

        if hasattr(self, "result"):
            return self.result
        self._marks = self._get_marks()

        if self._marks:
            self.result = False
            for mark in self._marks:
                self._mark = mark
                if "condition" in mark.kwargs:
                    args = (mark.kwargs["condition"],)
                else:
                    args = mark.args

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
        """
        Retrieve a specific attribute from the `_mark` dictionary.
        
        This method checks if the `_mark` attribute is `None`. If it is, the method returns the `default` value. Otherwise, it retrieves the value associated with the given `attr` from the `_mark.kwargs` dictionary. If the `attr` is not found, it returns the `default` value.
        
        Parameters:
        attr (str): The key in the `_mark.kwargs` dictionary to retrieve.
        default (Any, optional
        """

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
return "condition: " + str(self.expr)
        return expl
