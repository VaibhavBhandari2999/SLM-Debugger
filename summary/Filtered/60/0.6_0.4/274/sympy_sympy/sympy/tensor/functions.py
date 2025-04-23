from sympy import Expr, S, Mul, sympify
from sympy.core.compatibility import Iterable
from sympy.core.parameters import global_parameters


class TensorProduct(Expr):
    """
    Generic class for tensor products.
    """
    is_number = False

    def __new__(cls, *args, **kwargs):
        """
        Constructs a new tensor product expression.
        
        This function is the `__new__` method for creating instances of tensor product expressions. It takes multiple arguments, which can be SymPy expressions, iterables, matrices, or matrix expressions. The function processes these arguments to form a tensor product and optionally evaluates the result.
        
        Parameters:
        - *args: Variable length argument list of SymPy expressions, iterables, matrices, or matrix expressions.
        - **kwargs: Arbitrary keyword arguments. The key 'evaluate'
        """

        from sympy.tensor.array import NDimArray, tensorproduct, Array
        from sympy import MatrixBase, MatrixExpr
        from sympy.strategies import flatten

        args = [sympify(arg) for arg in args]
        evaluate = kwargs.get("evaluate", global_parameters.evaluate)

        if not evaluate:
            obj = Expr.__new__(cls, *args)
            return obj

        arrays = []
        other = []
        scalar = S.One
        for arg in args:
            if isinstance(arg, (Iterable, MatrixBase, NDimArray)):
                arrays.append(Array(arg))
            elif isinstance(arg, (MatrixExpr,)):
                other.append(arg)
            else:
                scalar *= arg

        coeff = scalar*tensorproduct(*arrays)
        if len(other) == 0:
            return coeff
        if coeff != 1:
            newargs = [coeff] + other
        else:
            newargs = other
        obj = Expr.__new__(cls, *newargs, **kwargs)
        return flatten(obj)

    def rank(self):
        return len(self.shape)

    def _get_args_shapes(self):
        from sympy import Array
        return [i.shape if hasattr(i, "shape") else Array(i).shape for i in self.args]

    @property
    def shape(self):
        shape_list = self._get_args_shapes()
        return sum(shape_list, ())

    def __getitem__(self, index):
        """
        Retrieve elements from the tensor based on the given index.
        
        Parameters:
        index (iterable): An iterable that provides indices for each argument in the multiplication.
        
        Returns:
        Mul: A new Mul object with elements selected according to the provided indices.
        
        This method allows for indexing into the tensor represented by the Mul object, using an iterable to specify the indices for each argument in the multiplication.
        The resulting object is a new Mul object with the selected elements.
        """

        index = iter(index)
        return Mul.fromiter(
            arg.__getitem__(tuple(next(index) for i in shp))
            for arg, shp in zip(self.args, self._get_args_shapes())
        )
