from sympy.core.compatibility import Iterable
from sympy.core.evaluate import global_evaluate
from sympy import Expr, S, Mul, sympify


class TensorProduct(Expr):
    """
    Generic class for tensor products.
    """
    is_number = False

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the class.
        
        This method is called when a new instance of the class is created. It processes the input arguments to construct a new object. The method supports the following:
        
        - `args`: A variable number of arguments which can be SymPy expressions, iterables, or matrix expressions.
        - `evaluate`: A boolean keyword argument that, if set to `False`, prevents the automatic evaluation of the expression. By default, it is set to the value of `global_evaluate
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
