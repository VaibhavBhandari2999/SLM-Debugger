import functools, itertools
from sympy.core.sympify import _sympify, sympify
from sympy.core.expr import Expr
from sympy.core import Basic, Tuple
from sympy.tensor.array import ImmutableDenseNDimArray
from sympy.core.symbol import Symbol
from sympy.core.numbers import Integer


class ArrayComprehension(Basic):
    """
    Generate a list comprehension.

    Explanation
    ===========

    If there is a symbolic dimension, for example, say [i for i in range(1, N)] where
    N is a Symbol, then the expression will not be expanded to an array. Otherwise,
    calling the doit() function will launch the expansion.

    Examples
    ========

    >>> from sympy.tensor.array import ArrayComprehension
    >>> from sympy import symbols
    >>> i, j, k = symbols('i j k')
    >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
    >>> a
    ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
    >>> a.doit()
    [[11, 12, 13], [21, 22, 23], [31, 32, 33], [41, 42, 43]]
    >>> b = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, k))
    >>> b.doit()
    ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, k))
    """
    def __new__(cls, function, *symbols, **assumptions):
        """
        Create a new ArrayComprehension object.
        
        This function initializes a new instance of the ArrayComprehension class with a given function and symbols representing the lower and upper bounds for the expression. The function also validates the input symbols to ensure they are correctly formatted and calculates the shape and rank of the resulting array.
        
        Parameters:
        function (str or SymPy expression): The function to be applied to each element in the array.
        symbols (tuple): A tuple of tuples, where each inner tuple contains
        """

        if any(len(l) != 3 or None for l in symbols):
            raise ValueError('ArrayComprehension requires values lower and upper bound'
                              ' for the expression')
        arglist = [sympify(function)]
        arglist.extend(cls._check_limits_validity(function, symbols))
        obj = Basic.__new__(cls, *arglist, **assumptions)
        obj._limits = obj._args[1:]
        obj._shape = cls._calculate_shape_from_limits(obj._limits)
        obj._rank = len(obj._shape)
        obj._loop_size = cls._calculate_loop_size(obj._shape)
        return obj

    @property
    def function(self):
        """The function applied across limits.

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j = symbols('i j')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> a.function
        10*i + j
        """
        return self._args[0]

    @property
    def limits(self):
        """
        The list of limits that will be applied while expanding the array.

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j = symbols('i j')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> a.limits
        ((i, 1, 4), (j, 1, 3))
        """
        return self._limits

    @property
    def free_symbols(self):
        """
        The set of the free_symbols in the array.
        Variables appeared in the bounds are supposed to be excluded
        from the free symbol set.

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j, k = symbols('i j k')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> a.free_symbols
        set()
        >>> b = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, k+3))
        >>> b.free_symbols
        {k}
        """
        expr_free_sym = self.function.free_symbols
        for var, inf, sup in self._limits:
            expr_free_sym.discard(var)
            curr_free_syms = inf.free_symbols.union(sup.free_symbols)
            expr_free_sym = expr_free_sym.union(curr_free_syms)
        return expr_free_sym

    @property
    def variables(self):
        """The tuples of the variables in the limits.

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j, k = symbols('i j k')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> a.variables
        [i, j]
        """
        return [l[0] for l in self._limits]

    @property
    def bound_symbols(self):
        """The list of dummy variables.

        Note
        ====

        Note that all variables are dummy variables since a limit without
        lower bound or upper bound is not accepted.
        """
        return [l[0] for l in self._limits if len(l) != 1]

    @property
    def shape(self):
        """
        The shape of the expanded array, which may have symbols.

        Note
        ====

        Both the lower and the upper bounds are included while
        calculating the shape.

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j, k = symbols('i j k')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> a.shape
        (4, 3)
        >>> b = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, k+3))
        >>> b.shape
        (4, k + 3)
        """
        return self._shape

    @property
    def is_shape_numeric(self):
        """
        Test if the array is shape-numeric which means there is no symbolic
        dimension.

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j, k = symbols('i j k')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> a.is_shape_numeric
        True
        >>> b = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, k+3))
        >>> b.is_shape_numeric
        False
        """
        for _, inf, sup in self._limits:
            if Basic(inf, sup).atoms(Symbol):
                return False
        return True

    def rank(self):
        """The rank of the expanded array.

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j, k = symbols('i j k')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> a.rank()
        2
        """
        return self._rank

    def __len__(self):
        """
        The length of the expanded array which means the number
        of elements in the array.

        Raises
        ======

        ValueError : When the length of the array is symbolic

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j = symbols('i j')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> len(a)
        12
        """
        if self._loop_size.free_symbols:
            raise ValueError('Symbolic length is not supported')
        return self._loop_size

    @classmethod
    def _check_limits_validity(cls, function, limits):
        #limits = sympify(limits)
        new_limits = []
        for var, inf, sup in limits:
            var = _sympify(var)
            inf = _sympify(inf)
            #since this is stored as an argument, it should be
            #a Tuple
            if isinstance(sup, list):
                sup = Tuple(*sup)
            else:
                sup = _sympify(sup)
            new_limits.append(Tuple(var, inf, sup))
            if any((not isinstance(i, Expr)) or i.atoms(Symbol, Integer) != i.atoms()
                                                                for i in [inf, sup]):
                raise TypeError('Bounds should be an Expression(combination of Integer and Symbol)')
            if (inf > sup) == True:
                raise ValueError('Lower bound should be inferior to upper bound')
            if var in inf.free_symbols or var in sup.free_symbols:
                raise ValueError('Variable should not be part of its bounds')
        return new_limits

    @classmethod
    def _calculate_shape_from_limits(cls, limits):
        return tuple([sup - inf + 1 for _, inf, sup in limits])

    @classmethod
    def _calculate_loop_size(cls, shape):
        """
        Calculate the loop size of a given shape.
        
        Args:
        shape (list): A list of integers representing the dimensions of a shape.
        
        Returns:
        int: The loop size, which is the product of all dimensions in the shape.
        
        Note:
        - If the shape is empty, the function returns 0.
        """

        if not shape:
            return 0
        loop_size = 1
        for l in shape:
            loop_size = loop_size * l

        return loop_size

    def doit(self):
        if not self.is_shape_numeric:
            return self

        return self._expand_array()

    def _expand_array(self):
        """
        Expand the array based on given limits.
        
        This function generates an array of elements based on the provided limits for each dimension. Each limit is a tuple (inf, sup) defining the inclusive range for that dimension.
        
        Parameters:
        self (ImmutableDenseNDimArray): The current instance of the array from which to generate the expanded array.
        
        Returns:
        ImmutableDenseNDimArray: A new array containing all possible combinations of elements within the specified ranges.
        
        Note:
        The function uses `it
        """

        res = []
        for values in itertools.product(*[range(inf, sup+1)
                                        for var, inf, sup
                                        in self._limits]):
            res.append(self._get_element(values))

        return ImmutableDenseNDimArray(res, self.shape)

    def _get_element(self, values):
        temp = self.function
        for var, val in zip(self.variables, values):
            temp = temp.subs(var, val)
        return temp

    def tolist(self):
        """Transform the expanded array to a list.

        Raises
        ======

        ValueError : When there is a symbolic dimension

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j = symbols('i j')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> a.tolist()
        [[11, 12, 13], [21, 22, 23], [31, 32, 33], [41, 42, 43]]
        """
        if self.is_shape_numeric:
            return self._expand_array().tolist()

        raise ValueError("A symbolic array cannot be expanded to a list")

    def tomatrix(self):
        """Transform the expanded array to a matrix.

        Raises
        ======

        ValueError : When there is a symbolic dimension
        ValueError : When the rank of the expanded array is not equal to 2

        Examples
        ========

        >>> from sympy.tensor.array import ArrayComprehension
        >>> from sympy import symbols
        >>> i, j = symbols('i j')
        >>> a = ArrayComprehension(10*i + j, (i, 1, 4), (j, 1, 3))
        >>> a.tomatrix()
        Matrix([
        [11, 12, 13],
        [21, 22, 23],
        [31, 32, 33],
        [41, 42, 43]])
        """
        from sympy.matrices import Matrix

        if not self.is_shape_numeric:
            raise ValueError("A symbolic array cannot be expanded to a matrix")
        if self._rank != 2:
            raise ValueError('Dimensions must be of size of 2')

        return Matrix(self._expand_array().tomatrix())


def isLambda(v):
    LAMBDA = lambda: 0
    return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__

class ArrayComprehensionMap(ArrayComprehension):
    '''
    A subclass of ArrayComprehension dedicated to map external function lambda.

    Notes
    =====

    Only the lambda function is considered.
    At most one argument in lambda function is accepted in order to avoid ambiguity
    in value assignment.

    Examples
    ========

    >>> from sympy.tensor.array import ArrayComprehensionMap
    >>> from sympy import symbols
    >>> i, j, k = symbols('i j k')
    >>> a = ArrayComprehensionMap(lambda: 1, (i, 1, 4))
    >>> a.doit()
    [1, 1, 1, 1]
    >>> b = ArrayComprehensionMap(lambda a: a+1, (j, 1, 4))
    >>> b.doit()
    [2, 3, 4, 5]

    '''
    def __new__(cls, function, *symbols, **assumptions):
        """
        Create a new ArrayComprehension object.
        
        This function initializes a new instance of the ArrayComprehension class with a given lambda function and symbol limits. The function validates the input parameters and calculates the shape and rank of the resulting array.
        
        Parameters:
        function (lambda): A lambda function representing the expression to be evaluated.
        *symbols (tuple): A tuple of tuples, where each inner tuple contains three elements: the lower bound, the upper bound, and the variable name for the loop.
        """

        if any(len(l) != 3 or None for l in symbols):
            raise ValueError('ArrayComprehension requires values lower and upper bound'
                              ' for the expression')

        if not isLambda(function):
            raise ValueError('Data type not supported')

        arglist = cls._check_limits_validity(function, symbols)
        obj = Basic.__new__(cls, *arglist, **assumptions)
        obj._limits = obj._args
        obj._shape = cls._calculate_shape_from_limits(obj._limits)
        obj._rank = len(obj._shape)
        obj._loop_size = cls._calculate_loop_size(obj._shape)
        obj._lambda = function
        return obj

    @property
    def func(self):
        """
        Generate an ArrayComprehensionMap instance with a specific lambda function.
        
        This method creates a new instance of ArrayComprehensionMap using a provided lambda function. The lambda function is applied to each element of the input array to generate a new array.
        
        Parameters:
        self (object): The object instance that calls this method.
        
        Returns:
        ArrayComprehensionMap: A new instance of ArrayComprehensionMap initialized with the provided lambda function.
        """

        class _(ArrayComprehensionMap):
            def __new__(cls, *args, **kwargs):
                return ArrayComprehensionMap(self._lambda, *args, **kwargs)
        return _

    def _get_element(self, values):
        """
        Retrieve the result of the lambda function.
        
        This method evaluates the lambda function with the provided values. If the lambda function takes no arguments, it is called without any arguments. If it takes one argument, the argument is set to the product of all values provided.
        
        Parameters:
        values (list): A list of numeric values to be used as arguments for the lambda function.
        
        Returns:
        The result of the lambda function evaluation.
        
        Example:
        >>> _get_element([2, 3, 4
        """

        temp = self._lambda
        if self._lambda.__code__.co_argcount == 0:
            temp = temp()
        elif self._lambda.__code__.co_argcount == 1:
            temp = temp(functools.reduce(lambda a, b: a*b, values))
        return temp
