from __future__ import print_function, division

from sympy.core import S
from sympy.core.relational import Eq, Ne
from sympy.logic.boolalg import BooleanFunction
from sympy.utilities.misc import func_name


class Contains(BooleanFunction):
    """
    Asserts that x is an element of the set S

    Examples
    ========

    >>> from sympy import Symbol, Integer, S
    >>> from sympy.sets.contains import Contains
    >>> Contains(Integer(2), S.Integers)
    True
    >>> Contains(Integer(-2), S.Naturals)
    False
    >>> i = Symbol('i', integer=True)
    >>> Contains(i, S.Naturals)
    Contains(i, Naturals)

    References
    ==========

    .. [1] https://en.wikipedia.org/wiki/Element_%28mathematics%29
    """
    @classmethod
    def eval(cls, x, s):
        """
        Evaluates whether the given value x is contained within the set s.
        
        Parameters:
        x (object): The value to check for membership in the set.
        s (Set): The set to check membership against.
        
        Returns:
        bool or Set: Returns True if x is in s, False if x is not in s, or a Set if the result is ambiguous.
        
        Raises:
        TypeError: If s is not an instance of Set.
        """

        from sympy.sets.sets import Set

        if not isinstance(s, Set):
            raise TypeError('expecting Set, not %s' % func_name(s))

        ret = s.contains(x)
        if not isinstance(ret, Contains) and (
                ret in (S.true, S.false) or isinstance(ret, Set)):
            return ret

    @property
    def binary_symbols(self):
        """
        Generates a set of binary symbols from the given expression.
        
        This function takes a logical expression and returns a set of all binary symbols (Boolean or Symbol instances, or symbols from Eq or Ne instances) present in the expression.
        
        Parameters:
        self (Expr): The logical expression from which to extract binary symbols.
        
        Returns:
        set: A set of binary symbols found in the expression.
        
        Example:
        >>> from sympy import Eq, Ne
        >>> expr = Eq(Symbol('x'), True)
        """

        return set().union(*[i.binary_symbols
            for i in self.args[1].args
            if i.is_Boolean or i.is_Symbol or
            isinstance(i, (Eq, Ne))])

    def as_set(self):
        return self
