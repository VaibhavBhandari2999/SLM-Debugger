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
        
        This function creates a new IndexedIntegral object from a given function and specified limits. The function also processes the limits to handle indexed expressions.
        
        Parameters:
        function (sympy expression): The function to be integrated.
        *limits (tuple): The integration limits. These can include indexed expressions.
        **assumptions (dict): Additional assumptions for the integration process.
        
        Returns:
        IndexedIntegral: A new IndexedIntegral object with the processed function and limits.
        
        Attributes
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
        Process a list of limits, converting indexed variables to dummy variables.
        
        This function processes a list of limits, converting any indexed variables to dummy variables. It returns a dictionary mapping the original indexed variables to the dummy variables and a new list of processed limits.
        
        Parameters:
        limits (list): A list of limits, where each limit can be a tuple, list, or Indexed object.
        
        Returns:
        tuple: A tuple containing two elements:
        - dict: A dictionary where keys are the original indexed variables
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
