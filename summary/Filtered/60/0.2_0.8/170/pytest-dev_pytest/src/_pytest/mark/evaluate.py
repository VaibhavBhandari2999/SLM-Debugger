import os
import platform
import sys
import traceback

import six

from ..outcomes import fail
from ..outcomes import TEST_OUTCOME


def cached_eval(config, expr, d):
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
        raises = self.get("raises")
        if not raises:
            return
        return not isinstance(exc, raises)

    def istrue(self):
        """
        Evaluates a test expression and returns the result. If an exception occurs during evaluation, it captures the error, formats an error message, and fails the test with the error details. The function handles specific exceptions like `TEST_OUTCOME` and `SyntaxError`, providing detailed error messages for syntax errors.
        
        Parameters:
        self (TestInstance): The current test instance containing the expression to evaluate.
        
        Returns:
        bool: True if the expression evaluates to True, False otherwise.
        
        Raises:
        Exception:
        """

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
        
        This function compiles a dictionary of global variables and attributes needed for evaluating expressions. The dictionary includes standard library modules like `os`, `sys`, and `platform`, as well as the configuration object from the item's context. If the item has an associated object, the global namespace of that object is also included.
        
        Returns:
        dict: A dictionary containing the global namespace for the current item.
        """

        d = {"os": os, "sys": sys, "platform": platform, "config": self.item.config}
        if hasattr(self.item, "obj"):
            d.update(self.item.obj.__globals__)
        return d

    def _istrue(self):
        """
        Function to determine the truth value of a test case based on evaluation of conditions.
        
        This function checks the truth value of a test case by evaluating a series of conditions. It first checks if the `result` attribute is already set. If not, it retrieves marks associated with the test case and evaluates each condition. If any condition evaluates to `True`, the function sets the `result` attribute to `True` and stores the reason and expression used. If no conditions evaluate to `True`, the function
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
