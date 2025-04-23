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
        Evaluates whether a given value x is contained within the set s.
        
        Parameters:
        x (object): The value to check for membership in the set.
        s (Set): The set to check membership against.
        
        Returns:
        bool or Set: Returns True if x is in s, False if x is not in s, or the set itself if the result is a set.
        
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
        Generate a set of binary symbols from the given logical expression.
        
        This function takes a logical expression and returns a set of all binary symbols
        present in the expression. A binary symbol is a symbol that appears in a binary
        logical operation (like AND, OR, etc.) within the expression.
        
        Parameters:
        self (Expr): The logical expression from which to extract binary symbols.
        
        Returns:
        set: A set of binary symbols found in the expression.
        
        Example:
        >>> expr = (A & B
        """

        return set().union(*[i.binary_symbols
            for i in self.args[1].args
            if i.is_Boolean or i.is_Symbol or
            isinstance(i, (Eq, Ne))])

    def as_set(self):
        raise NotImplementedError()
