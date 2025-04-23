from sympy.tensor import Indexed
from sympy.core.containers import Tuple
from sympy.core.symbol import Dummy
from sympy.core.sympify import sympify
from sympy.integrals.integrals import Integral


class IndexedIntegral(Integral):
    """
    Experimental class to test integration by indexed variables.

    Usage is analogue to ``Integral``, it simply adds awareness of
    integration over indices.

    Contraction of non-identical index symbols referring to the same
    ``IndexedBase`` is not yet supported.

    Examples
    ========

    >>> from sympy.sandbox.indexed_integrals import IndexedIntegral
    >>> from sympy import IndexedBase, symbols
    >>> A = IndexedBase('A')
    >>> i, j = symbols('i j', integer=True)
    >>> ii = IndexedIntegral(A[i], A[i])
    >>> ii
    Integral(_A[i], _A[i])
    >>> ii.doit()
    A[i]**2/2

    If the indices are different, indexed objects are considered to be
    different variables:

    >>> i2 = IndexedIntegral(A[j], A[i])
    >>> i2
    Integral(A[j], _A[i])
    >>> i2.doit()
    A[i]*A[j]
    """

    def __new__(cls, function, *limits, **assumptions):
        """
        Create a new IndexedIntegral object.
        
        This method initializes a new IndexedIntegral object with the given function and limits. The function is first converted to a SymPy expression and then processed to handle indexed variables. The limits are also processed to handle indexed integration limits.
        
        Parameters:
        function (sympify-able expression): The function to be integrated.
        *limits: Variable number of limits for the integration. Each limit should be a tuple (variable, start, end).
        **assumptions:
        """

        repl, limits = IndexedIntegral._indexed_process_limits(limits)
        function = sympify(function)
        function = function.xreplace(repl)
        obj = Integral.__new__(cls, function, *limits, **assumptions)
        obj._indexed_repl = repl
        obj._indexed_reverse_repl = {val: key for key, val in repl.items()}
        return obj

    def doit(self):
        res = super().doit()
        return res.xreplace(self._indexed_reverse_repl)

    @staticmethod
    def _indexed_process_limits(limits):
        repl = {}
        newlimits = []
        for i in limits:
            if isinstance(i, (tuple, list, Tuple)):
                v = i[0]
                vrest = i[1:]
            else:
                v = i
                vrest = ()
            if isinstance(v, Indexed):
                if v not in repl:
                    r = Dummy(str(v))
                    repl[v] = r
                newlimits.append((r,)+vrest)
            else:
                newlimits.append(i)
        return repl, newlimits
return repl, newlimits
