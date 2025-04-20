import os
import platform
import sys
import traceback

import six

from ..outcomes import fail
from ..outcomes import TEST_OUTCOME


def cached_eval(config, expr, d):
    """
    Evaluate an expression in a given context.
    
    This function evaluates an expression in the context of a given dictionary `d` and stores the result in a cache for future use. If the expression has been evaluated before, it retrieves the result from the cache.
    
    Parameters:
    config (object): The configuration object that holds the cache.
    expr (str): The expression to be evaluated.
    d (dict): The context in which the expression should be evaluated.
    
    Returns:
    The result of the evaluated expression
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


class MarkEvaluator(object):
    def __init__(self, item, name):
        self.item = item
        self._marks = None
        self._mark = None
        self._mark_name = name

    def __bool__(self):
        # dont cache here to prevent staleness
        return bool(self._get_marks())

    __nonzero__ = __bool__

    def wasvalid(self):
        return not hasattr(self, "exc")

    def _get_marks(self):
        return list(self.item.iter_markers(name=self._mark_name))

    def invalidraise(self, exc):
        """
        Determine if the given exception `exc` is not an instance of the specified exception types in the 'raises' attribute.
        
        Parameters:
        exc (Exception): The exception instance to check.
        
        Returns:
        bool: True if `exc` is not an instance of the specified exception types, False otherwise.
        
        Note:
        This function checks if the 'raises' attribute is set and if the provided `exc` is not an instance of the specified exception types. If 'raises' is not set,
        """

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
        """
        Retrieve the global namespace for the current item.
        
        This method constructs a dictionary of global variables and objects that are relevant to the current item. The dictionary includes standard library modules such as `os`, `sys`, and `platform`, as well as the `config` attribute from the item's configuration. If the item has an associated object, the global namespace of that object is also included in the dictionary.
        
        Returns:
        dict: A dictionary containing the global namespace for the current item.
        """

        d = {"os": os, "sys": sys, "platform": platform, "config": self.item.config}
        if hasattr(self.item, "obj"):
            d.update(self.item.obj.__globals__)
        return d

    def _istrue(self):
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
                    if isinstance(expr, six.string_types):
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
(self.expr)
        return expl
