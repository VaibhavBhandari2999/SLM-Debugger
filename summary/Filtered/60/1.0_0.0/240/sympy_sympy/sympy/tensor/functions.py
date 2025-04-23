import collections
from sympy.core.evaluate import global_evaluate
from sympy import Expr, S, Mul, sympify


class TensorProduct(Expr):
    """
    Generic class for tensor products.
    """
    is_number = False

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the tensor product of multiple arguments.
        
        This method is the `__new__` constructor for tensor product operations. It takes multiple arguments and combines them using the tensor product operation. The method handles different types of arguments and applies the `evaluate` flag to control the evaluation of the tensor product.
        
        Parameters:
        - cls: The class of the object being created.
        - *args: Variable length argument list, where each argument can be a SymPy expression, a SymPy tensor,
        """

        from sympy.tensor.array import NDimArray, tensorproduct, Array
        from sympy import MatrixBase, MatrixExpr
        from sympy.strategies import flatten

        args = [sympify(arg) for arg in args]
        evaluate = kwargs.get("evaluate", global_evaluate[0])

        if not evaluate:
            obj = Expr.__new__(cls, *args)
            return obj

        arrays = []
        other = []
        scalar = S.One
        for arg in args:
            if isinstance(arg, (collections.Iterable, MatrixBase, NDimArray)):
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
