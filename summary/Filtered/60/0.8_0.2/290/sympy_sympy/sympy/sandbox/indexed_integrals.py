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
        
        This method is used to create a new instance of the IndexedIntegral class. It processes the given function and limits, and sets up the necessary attributes for the new object.
        
        Parameters:
        function (sympy expression): The function to be integrated.
        *limits (tuple): Variable limits for the integration. Each limit is a tuple of the form (symbol, start, end).
        **assumptions (dict): Additional assumptions for the integration process.
        
        Returns
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
        """
        Process a list of limits to handle indexed variables.
        
        This function takes a list of limits and processes it to handle indexed variables. It replaces each indexed variable with a dummy variable and returns a dictionary mapping the original indexed variables to the dummy variables, along with the processed list of limits.
        
        Parameters:
        limits (list): A list of limits, where each limit can be a tuple, list, or a single value. Indexed variables within the limits are to be replaced.
        
        Returns:
        tuple: A tuple
        """

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
