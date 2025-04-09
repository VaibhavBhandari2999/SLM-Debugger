import os
import platform
import sys
import traceback

from ..outcomes import fail
from ..outcomes import TEST_OUTCOME


def cached_eval(config, expr, d):
    """
    Evaluates an expression using the provided configuration and dictionary.
    
    Args:
    config (object): The configuration object containing the `_evalcache` attribute.
    expr (str): The expression to be evaluated.
    d (dict): The dictionary containing the context for evaluation.
    
    Returns:
    Any: The result of evaluating the expression.
    
    Summary:
    This function uses the `_evalcache` attribute of the `config` object to cache the results of previously evaluated expressions. If the expression is
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
        """
        Initialize a new instance of the class.
        
        Args:
        item (str): The item to be associated with the instance.
        name (str): The name of the mark.
        
        Attributes:
        item (str): The item associated with the instance.
        _marks (dict): A dictionary to store marks.
        _mark (float): The current mark.
        _mark_name (str): The name of the mark.
        """

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
        """
        Determines whether an exception is valid based on the specified raises attribute.
        
        Args:
        exc (Exception): The exception instance to check.
        
        Returns:
        bool: True if the exception is not an instance of the specified raises attribute, False otherwise.
        """

        raises = self.get("raises")
        if not raises:
            return
        return not isinstance(exc, raises)

    def istrue(self):
        """
        Evaluates the truthiness of an expression. If an error occurs during evaluation, it captures the exception, formats an error message, and fails the test with the formatted message. The function uses the following key components:
        
        - `self._istrue()`: Evaluates the expression and returns a boolean value.
        - `TEST_OUTCOME`: A custom exception class that might be raised during evaluation.
        - `sys.exc_info()`: Captures the current exception information.
        - `fail
        """

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
        """
        Retrieve the global namespace dictionary.
        
        This method constructs a dictionary containing various modules and
        attributes that are commonly used in the context of the current item's
        configuration and potentially its object's global namespace. The resulting
        dictionary is then returned as the global namespace.
        
        Args:
        None
        
        Returns:
        dict: A dictionary representing the global namespace, including
        essential modules like `os`, `sys`, and `platform`, along with
        the configuration from the current item
        """

        d = {"os": os, "sys": sys, "platform": platform, "config": self.item.config}
        if hasattr(self.item, "obj"):
            d.update(self.item.obj.__globals__)
        return d

    def _istrue(self):
        """
        _istrue(self) -> bool
        
        Determines whether a test should pass or fail based on evaluation of conditions.
        
        This method checks if an attribute `result` exists. If it does, it returns its value.
        Otherwise, it initializes `_marks` by calling `_get_marks()`. It then iterates over each mark in `_marks`, evaluating conditions specified within the marks. The evaluation can involve string expressions that are evaluated using `cached_eval` or boolean values directly. If any condition evaluates
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
        Retrieve a keyword argument from the mark's kwargs dictionary.
        
        Args:
        attr (str): The attribute name to retrieve.
        default (Any, optional): The default value to return if the attribute is not found. Defaults to None.
        
        Returns:
        Any: The value of the attribute if found; otherwise, the default value.
        
        Notes:
        - This method checks if the `_mark` attribute is `None`. If it is, it returns the `default` value.
        -
        """

        if self._mark is None:
            return default
        return self._mark.kwargs.get(attr, default)

    def getexplanation(self):
        """
        Get the explanation for the condition.
        
        Args:
        None
        
        Returns:
        str: The explanation for the condition.
        
        Raises:
        None
        
        Notes:
        - Uses `getattr` and `self.get` to retrieve the 'reason' attribute or dictionary key.
        - If 'reason' is not found, checks if 'expr' attribute exists and returns a string based on it.
        """

        expl = getattr(self, "reason", None) or self.get("reason", None)
        if not expl:
            if not hasattr(self, "expr"):
                return ""
            else:
                return "condition: " + str(self.expr)
        return expl
