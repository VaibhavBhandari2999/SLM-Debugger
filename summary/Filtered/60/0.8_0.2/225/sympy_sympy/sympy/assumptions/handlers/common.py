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
        Determine if the given expression is basic (i.e., commutative).
        
        This function checks if the provided expression is basic, which means all its arguments are commutative under the given assumptions.
        
        Parameters:
        expr (Expr): The expression to check for basicness.
        assumptions (Assumptions): The assumptions to be considered when checking the commutativity of the expression's arguments.
        
        Returns:
        bool: True if the expression is basic (all arguments are commutative), False otherwise.
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
        """
        Generate the negation of a logical expression.
        
        This function evaluates the negation of a given logical expression under a set of assumptions.
        
        Parameters:
        expr (sympy expression): The logical expression to be negated.
        assumptions (AssumptionsSet, optional): A set of assumptions to be used during evaluation. Defaults to None.
        
        Returns:
        bool or None: The negated value of the expression if it can be determined (True or False), otherwise None.
        
        Example:
        >>> from
        """

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
        Determine if an expression is true under given assumptions.
        
        This function evaluates whether the given logical expression `expr` is true
        under the specified `assumptions`. It iterates over each argument in the
        expression and checks the truth value of each argument using the `ask` function.
        If any argument is found to be false, the function immediately returns False.
        If an argument cannot be determined (returns None), the overall result is set
        to None. If all arguments are true, the function
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
for a in expr.args), quick_exit=True)
t=True)
