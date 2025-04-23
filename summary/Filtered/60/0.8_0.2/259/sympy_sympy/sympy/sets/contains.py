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
        - x: The value to check for membership in the set.
        - s: The set to check membership against, expected to be an instance of sympy.sets.sets.Set.
        
        Returns:
        - A boolean value (True or False) if the membership can be determined directly.
        - A sympy.sets.contains.Contains object if the membership cannot be determined directly but is known to be a member or non-member.
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
        Generate a set of binary symbols used in the given Boolean expression or symbols.
        
        This function takes a Boolean expression or a set of symbols and returns a set of binary symbols (Boolean symbols or symbols from equality or inequality expressions) present in the expression.
        
        Parameters:
        self (Expression): The current instance of the expression or the expression itself.
        
        Returns:
        set: A set of binary symbols found in the expression.
        
        Example:
        >>> expr = (x & y) | (z == a) |
        """

        return set().union(*[i.binary_symbols
            for i in self.args[1].args
            if i.is_Boolean or i.is_Symbol or
            isinstance(i, (Eq, Ne))])

    def as_set(self):
        return self
