from sympy.core.logic import _fuzzy_group
from sympy.logic.boolalg import conjuncts
from sympy.assumptions import Q, ask


class AskHandler(object):
    """Base class that all Ask Handlers must inherit"""
    pass


class CommonHandler(AskHandler):
    """Defines some useful methods common to most Handlers """

    @staticmethod
    def AlwaysTrue(expr, assumptions):
        return True

    @staticmethod
    def AlwaysFalse(expr, assumptions):
        return False

    NaN = AlwaysFalse


class AskCommutativeHandler(CommonHandler):
    """
    Handler for key 'commutative'
    """

    @staticmethod
    def Symbol(expr, assumptions):
        """Objects are expected to be commutative unless otherwise stated"""
        assumps = conjuncts(assumptions)
        if expr.is_commutative is not None:
            return expr.is_commutative and not ~Q.commutative(expr) in assumps
        if Q.commutative(expr) in assumps:
            return True
        elif ~Q.commutative(expr) in assumps:
            return False
        return True

    @staticmethod
    def Basic(expr, assumptions):
        """
        Determine if an expression is basic (commutative).
        
        This function checks if all arguments in the given expression are commutative.
        It returns `True` if all arguments are commutative, otherwise `False`.
        
        Parameters:
        - expr (Expression): The expression to check for commutativity of its arguments.
        - assumptions (Assumptions): Assumptions about the symbols in the expression.
        
        Returns:
        - bool: `True` if all arguments in the expression are commutative, `
        """

        for arg in expr.args:
            if not ask(Q.commutative(arg), assumptions):
                return False
        return True

    Number, NaN = [staticmethod(CommonHandler.AlwaysTrue)]*2


class TautologicalHandler(AskHandler):
    """Wrapper allowing to query the truth value of a boolean expression."""

    @staticmethod
    def bool(expr, assumptions):
        return expr

    BooleanTrue = staticmethod(CommonHandler.AlwaysTrue)
    BooleanFalse = staticmethod(CommonHandler.AlwaysFalse)

    @staticmethod
    def AppliedPredicate(expr, assumptions):
        return ask(expr, assumptions)

    @staticmethod
    def Not(expr, assumptions):
        value = ask(expr.args[0], assumptions=assumptions)
        if value in (True, False):
            return not value
        else:
            return None

    @staticmethod
    def Or(expr, assumptions):
        result = False
        for arg in expr.args:
            p = ask(arg, assumptions=assumptions)
            if p is True:
                return True
            if p is None:
                result = None
        return result

    @staticmethod
    def And(expr, assumptions):
        """
        Determine if a logical expression is true under given assumptions.
        
        This function evaluates a logical expression `expr` by checking each of its
        arguments against the given `assumptions`. It returns `False` if any argument
        evaluates to `False` under the assumptions. If an argument cannot be determined
        to be `True` or `False` under the assumptions, the function returns `None`.
        If all arguments are `True`, it returns `True`.
        
        Parameters:
        expr (symp
        """

        result = True
        for arg in expr.args:
            p = ask(arg, assumptions=assumptions)
            if p is False:
                return False
            if p is None:
                result = None
        return result

    @staticmethod
    def Implies(expr, assumptions):
        p, q = expr.args
        return ask(~p | q, assumptions=assumptions)

    @staticmethod
    def Equivalent(expr, assumptions):
        """
        Determine if two logical expressions are equivalent under given assumptions.
        
        This function checks if two logical expressions, `p` and `q`, are equivalent
        under the given logical assumptions. It uses the `ask` function to evaluate
        the truth value of `p` and `q` under the provided assumptions.
        
        Parameters:
        expr (tuple): A tuple containing two logical expressions (p, q).
        assumptions (Assumptions): A set of logical assumptions under which the
        expressions are evaluated
        """

        p, q = expr.args
        pt = ask(p, assumptions=assumptions)
        if pt is None:
            return None
        qt = ask(q, assumptions=assumptions)
        if qt is None:
            return None
        return pt == qt


#### Helper methods
def test_closed_group(expr, assumptions, key):
    """
    Test for membership in a group with respect
    to the current operation
    """
    return _fuzzy_group(
        (ask(key(a), assumptions) for a in expr.args), quick_exit=True)
