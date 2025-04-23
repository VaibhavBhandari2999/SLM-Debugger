from distutils.version import LooseVersion as V

from sympy import Mul
from sympy.core.compatibility import Iterable
from sympy.external import import_module
from sympy.printing.precedence import PRECEDENCE
from sympy.printing.pycode import AbstractPythonCodePrinter
import sympy


class TensorflowPrinter(AbstractPythonCodePrinter):
    """
    Tensorflow printer which handles vectorized piecewise functions,
    logical operators, max/min, and relational operators.
    """
    printmethod = "_tensorflowcode"

    mapping = {
        sympy.Abs: "tensorflow.abs",
        sympy.sign: "tensorflow.sign",
        sympy.ceiling: "tensorflow.ceil",
        sympy.floor: "tensorflow.floor",
        sympy.log: "tensorflow.log",
        sympy.exp: "tensorflow.exp",
        sympy.sqrt: "tensorflow.sqrt",
        sympy.cos: "tensorflow.cos",
        sympy.acos: "tensorflow.acos",
        sympy.sin: "tensorflow.sin",
        sympy.asin: "tensorflow.asin",
        sympy.tan: "tensorflow.tan",
        sympy.atan: "tensorflow.atan",
        sympy.atan2: "tensorflow.atan2",
        sympy.cosh: "tensorflow.cosh",
        sympy.acosh: "tensorflow.acosh",
        sympy.sinh: "tensorflow.sinh",
        sympy.asinh: "tensorflow.asinh",
        sympy.tanh: "tensorflow.tanh",
        sympy.atanh: "tensorflow.atanh",
        sympy.re: "tensorflow.real",
        sympy.im: "tensorflow.imag",
        sympy.arg: "tensorflow.angle",
        sympy.erf: "tensorflow.erf",
        sympy.loggamma: "tensorflow.gammaln",
        sympy.Pow: "tensorflow.pow",
        sympy.Eq: "tensorflow.equal",
        sympy.Ne: "tensorflow.not_equal",
        sympy.StrictGreaterThan: "tensorflow.greater",
        sympy.StrictLessThan: "tensorflow.less",
        sympy.LessThan: "tensorflow.less_equal",
        sympy.GreaterThan: "tensorflow.greater_equal",
        sympy.And: "tensorflow.logical_and",
        sympy.Or: "tensorflow.logical_or",
        sympy.Not: "tensorflow.logical_not",
        sympy.Max: "tensorflow.maximum",
        sympy.Min: "tensorflow.minimum",
        # Matrices
        sympy.MatAdd: "tensorflow.add",
        sympy.HadamardProduct: "tensorflow.multiply",
        sympy.Trace: "tensorflow.trace",
        sympy.Determinant : "tensorflow.matrix_determinant",
        sympy.Inverse: "tensorflow.matrix_inverse",
        sympy.Transpose: "tensorflow.matrix_transpose",
    }

    def _print_Function(self, expr):
        """
        Prints a Tensorflow expression.
        
        This function is used to print a Tensorflow expression. It checks if the type of the expression is in the mapping dictionary and retrieves the corresponding operation. If the operation is not found, it falls back to the default printing method for basic expressions. If the expression has one argument, it formats the operation and the argument into a string. If the expression has multiple arguments, it expands the binary operation and formats the arguments accordingly.
        
        Parameters:
        expr (Expression): The
        """

        op = self.mapping.get(type(expr), None)
        if op is None:
            return super(TensorflowPrinter, self)._print_Basic(expr)
        children = [self._print(arg) for arg in expr.args]
        if len(children) == 1:
            return "%s(%s)" % (
                self._module_format(op),
                children[0]
            )
        else:
            return self._expand_fold_binary_op(op, children)

    _print_Expr = _print_Function
    _print_Application = _print_Function
    _print_MatrixExpr = _print_Function
    # TODO: a better class structure would avoid this mess:
    _print_Not = _print_Function
    _print_And = _print_Function
    _print_Or = _print_Function
    _print_Transpose = _print_Function
    _print_Trace = _print_Function

    def _print_Derivative(self, expr):
        variables = expr.variables
        if any(isinstance(i, Iterable) for i in variables):
            raise NotImplementedError("derivation by multiple variables is not supported")
        def unfold(expr, args):
            if not args:
                return self._print(expr)
            return "%s(%s, %s)[0]" % (
                    self._module_format("tensorflow.gradients"),
                    unfold(expr, args[:-1]),
                    self._print(args[-1]),
                )
        return unfold(expr.expr, variables)

    def _print_Piecewise(self, expr):
        """
        Prints a TensorFlow expression for a given Piecewise function.
        
        This function takes a SymPy Piecewise expression and converts it into a TensorFlow-compatible expression. It handles both single and multiple conditions within the Piecewise function.
        
        Parameters:
        expr (Piecewise): The SymPy Piecewise expression to be converted.
        
        Returns:
        str: A string representing the TensorFlow expression for the given Piecewise function.
        
        Notes:
        - If TensorFlow is not installed or the version is less than 1.0, the
        """

        tensorflow = import_module('tensorflow')
        if tensorflow and V(tensorflow.__version__) < '1.0':
            tensorflow_piecewise = "select"
        else:
            tensorflow_piecewise = "where"

        from sympy import Piecewise
        e, cond = expr.args[0].args
        if len(expr.args) == 1:
            return '{0}({1}, {2}, {3})'.format(
                tensorflow_piecewise,
                self._print(cond),
                self._print(e),
                0)

        return '{0}({1}, {2}, {3})'.format(
            tensorflow_piecewise,
            self._print(cond),
            self._print(e),
            self._print(Piecewise(*expr.args[1:])))

    def _print_MatrixBase(self, expr):
        tensorflow_f = "tensorflow.Variable" if expr.free_symbols else "tensorflow.constant"
        data = "["+", ".join(["["+", ".join([self._print(j) for j in i])+"]" for i in expr.tolist()])+"]"
        return "%s(%s)" % (
            self._module_format(tensorflow_f),
            data,
        )

    def _print_MatMul(self, expr):
        from sympy.matrices.expressions import MatrixExpr
        mat_args = [arg for arg in expr.args if isinstance(arg, MatrixExpr)]
        args = [arg for arg in expr.args if arg not in mat_args]
        if args:
            return "%s*%s" % (
                self.parenthesize(Mul.fromiter(args), PRECEDENCE["Mul"]),
                self._expand_fold_binary_op("tensorflow.matmul", mat_args)
            )
        else:
            return self._expand_fold_binary_op("tensorflow.matmul", mat_args)

    def _print_MatPow(self, expr):
        return self._expand_fold_binary_op("tensorflow.matmul", [expr.base]*expr.exp)

    def _print_Assignment(self, expr):
        # TODO: is this necessary?
        return "%s = %s" % (
            self._print(expr.lhs),
            self._print(expr.rhs),
        )

    def _print_CodeBlock(self, expr):
        # TODO: is this necessary?
        ret = []
        for subexpr in expr.args:
            ret.append(self._print(subexpr))
        return "\n".join(ret)

    def _get_letter_generator_for_einsum(self):
        for i in range(97, 123):
            yield chr(i)
        for i in range(65, 91):
            yield chr(i)
        raise ValueError("out of letters")

    def _print_CodegenArrayTensorProduct(self, expr):
        array_list = [j for i, arg in enumerate(expr.args) for j in
                (self._print(arg), "[%i, %i]" % (2*i, 2*i+1))]
        letters = self._get_letter_generator_for_einsum()
        contraction_string = ",".join(["".join([next(letters) for j in range(i)]) for i in expr.subranks])
        return '%s("%s", %s)' % (
                self._module_format('tensorflow.einsum'),
                contraction_string,
                ", ".join([self._print(arg) for arg in expr.args])
        )

    def _print_CodegenArrayContraction(self, expr):
        from sympy.codegen.array_utils import CodegenArrayTensorProduct
        base = expr.expr
        contraction_indices = expr.contraction_indices
        contraction_string, letters_free, letters_dum = self._get_einsum_string(base.subranks, contraction_indices)

        if not contraction_indices:
            return self._print(base)
        if isinstance(base, CodegenArrayTensorProduct):
            elems = ["%s" % (self._print(arg)) for arg in base.args]
            return "%s(\"%s\", %s)" % (
                self._module_format("tensorflow.einsum"),
                contraction_string,
                ", ".join(elems)
            )
        raise NotImplementedError()

    def _print_CodegenArrayDiagonal(self, expr):
        from sympy.codegen.array_utils import CodegenArrayTensorProduct
        diagonal_indices = list(expr.diagonal_indices)
        if len(diagonal_indices) > 1:
            # TODO: this should be handled in sympy.codegen.array_utils,
            # possibly by creating the possibility of unfolding the
            # CodegenArrayDiagonal object into nested ones. Same reasoning for
            # the array contraction.
            raise NotImplementedError
        if len(diagonal_indices[0]) != 2:
            raise NotImplementedError
        if isinstance(expr.expr, CodegenArrayTensorProduct):
            subranks = expr.expr.subranks
            elems = expr.expr.args
        else:
            subranks = expr.subranks
            elems = [expr.expr]
        diagonal_string, letters_free, letters_dum = self._get_einsum_string(subranks, diagonal_indices)
        elems = [self._print(i) for i in elems]
        return '%s("%s", %s)' % (
            self._module_format("tensorflow.einsum"),
            "{0}->{1}{2}".format(diagonal_string, "".join(letters_free), "".join(letters_dum)),
            ", ".join(elems)
        )

    def _print_CodegenArrayPermuteDims(self, expr):
        return "%s(%s, %s)" % (
            self._module_format("tensorflow.transpose"),
            self._print(expr.expr),
            self._print(expr.permutation.args[0]),
        )

    def _print_CodegenArrayElementwiseAdd(self, expr):
        return self._expand_fold_binary_op('tensorflow.add', expr.args)


def tensorflow_code(expr):
    printer = TensorflowPrinter()
    return printer.doprint(expr)
r()
    return printer.doprint(expr)
   printer = TensorflowPrinter()
    return printer.doprint(expr)
