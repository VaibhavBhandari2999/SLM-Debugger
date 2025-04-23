from sympy import Expr, S, Mul, sympify
from sympy.core.compatibility import Iterable
from sympy.core.parameters import global_parameters


class TensorProduct(Expr):
    """
    Generic class for tensor products.
    """
    is_number = False

    def __new__(cls, *args, **kwargs):
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
        Retrieve elements from the tensor based on the given indices.
        
        This method allows for the retrieval of elements from a tensor by specifying
        indices for each of its dimensions. The indices are provided as an iterable,
        and the function iterates over the tensor's arguments to extract the desired
        elements.
        
        Parameters:
        index (iterable): An iterable of indices, one for each dimension of the tensor.
        
        Returns:
        Mul: A new tensor containing the elements specified by the given indices.
        
        Example:
        >>> tensor
        """

        index = iter(index)
        return Mul.fromiter(
            arg.__getitem__(tuple(next(index) for i in shp))
            for arg, shp in zip(self.args, self._get_args_shapes())
        )
