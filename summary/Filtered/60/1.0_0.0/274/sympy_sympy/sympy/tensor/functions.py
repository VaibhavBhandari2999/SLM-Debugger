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
        Create a new instance of the tensor product of multiple arguments.
        
        This function is the `__new__` method for creating instances of tensor products. It takes multiple arguments and keyword arguments. The function processes the arguments to determine which are arrays or matrix expressions, and which are scalar values. It then constructs a tensor product of the arrays and multiplies it by the scalar values. If no arrays are provided, it returns the tensor product of the scalar values. If the `evaluate` flag is set to
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
        index = iter(index)
        return Mul.fromiter(
            arg.__getitem__(tuple(next(index) for i in shp))
            for arg, shp in zip(self.args, self._get_args_shapes())
        )

            for arg, shp in zip(self.args, self._get_args_shapes())
        )
