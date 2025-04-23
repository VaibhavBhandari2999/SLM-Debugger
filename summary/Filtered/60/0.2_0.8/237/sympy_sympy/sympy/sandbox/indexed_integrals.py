from sympy.tensor import Indexed
from sympy import Integral, Dummy, sympify, Tuple


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
        
        This method is used to create a new instance of the IndexedIntegral class. It processes the input function and limits, and initializes the integral with the given function and limits.
        
        Parameters:
        function (sympy expression): The function to be integrated.
        *limits (tuple): The integration limits. Each limit is a tuple of the form (symbol, start, end).
        **assumptions (dict): Additional assumptions for the integral.
        
        Returns:
        Indexed
        """

        repl, limits = IndexedIntegral._indexed_process_limits(limits)
        function = sympify(function)
        function = function.xreplace(repl)
        obj = Integral.__new__(cls, function, *limits, **assumptions)
        obj._indexed_repl = repl
        obj._indexed_reverse_repl = dict((val, key) for key, val in repl.items())
        return obj

    def doit(self):
        res = super(IndexedIntegral, self).doit()
        return res.xreplace(self._indexed_reverse_repl)

    @staticmethod
    def _indexed_process_limits(limits):
        """
        Process a list of limits, handling indexed elements.
        
        This function processes a list of limits, which can be either individual values or tuples/lists containing an indexed element and additional arguments. It replaces indexed elements with dummy symbols and returns a dictionary mapping the original indexed elements to their dummy symbols, along with a new list of processed limits.
        
        Parameters:
        limits (list): A list of limits, where each limit can be an indexed element or a tuple/list containing an indexed element and additional arguments.
        
        Returns:
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
