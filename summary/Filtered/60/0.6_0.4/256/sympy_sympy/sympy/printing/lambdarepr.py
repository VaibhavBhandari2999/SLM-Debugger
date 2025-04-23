from __future__ import print_function, division
from .pycode import (
    PythonCodePrinter,
    MpmathPrinter,  # MpmathPrinter is imported for backward compatibility
    NumPyPrinter  # NumPyPrinter is imported for backward compatibility
)
from sympy.utilities import default_sort_key


class LambdaPrinter(PythonCodePrinter):
    """
    This printer converts expressions into strings that can be used by
    lambdify.
    """
    printmethod = "_lambdacode"


    def _print_And(self, expr):
        result = ['(']
        for arg in sorted(expr.args, key=default_sort_key):
            result.extend(['(', self._print(arg), ')'])
            result.append(' and ')
        result = result[:-1]
        result.append(')')
        return ''.join(result)

    def _print_Or(self, expr):
        """
        Prints the disjunction (logical OR) of the given logical expression.
        
        This function takes a logical expression and prints its disjunctive form, which is the logical OR of its arguments. The arguments are sorted and each is enclosed in parentheses. The function handles the logical OR operation and ensures that the output is properly formatted.
        
        Parameters:
        expr (Expr): The logical expression to be printed. The expression should be a disjunction of logical terms.
        
        Returns:
        str: A string representation of
        """

        result = ['(']
        for arg in sorted(expr.args, key=default_sort_key):
            result.extend(['(', self._print(arg), ')'])
            result.append(' or ')
        result = result[:-1]
        result.append(')')
        return ''.join(result)

    def _print_Not(self, expr):
        result = ['(', 'not (', self._print(expr.args[0]), '))']
        return ''.join(result)

    def _print_BooleanTrue(self, expr):
        return "True"

    def _print_BooleanFalse(self, expr):
        return "False"

    def _print_ITE(self, expr):
        result = [
            '((', self._print(expr.args[1]),
            ') if (', self._print(expr.args[0]),
            ') else (', self._print(expr.args[2]), '))'
        ]
        return ''.join(result)

    def _print_NumberSymbol(self, expr):
        return str(expr)


# numexpr works by altering the string passed to numexpr.evaluate
# rather than by populating a namespace.  Thus a special printer...
class NumExprPrinter(LambdaPrinter):
    # key, value pairs correspond to sympy name and numexpr name
    # functions not appearing in this dict will raise a TypeError
    printmethod = "_numexprcode"

    _numexpr_functions = {
        'sin' : 'sin',
        'cos' : 'cos',
        'tan' : 'tan',
        'asin': 'arcsin',
        'acos': 'arccos',
        'atan': 'arctan',
        'atan2' : 'arctan2',
        'sinh' : 'sinh',
        'cosh' : 'cosh',
        'tanh' : 'tanh',
        'asinh': 'arcsinh',
        'acosh': 'arccosh',
        'atanh': 'arctanh',
        'ln' : 'log',
        'log': 'log',
        'exp': 'exp',
        'sqrt' : 'sqrt',
        'Abs' : 'abs',
        'conjugate' : 'conj',
        'im' : 'imag',
        're' : 'real',
        'where' : 'where',
        'complex' : 'complex',
        'contains' : 'contains',
    }

    def _print_ImaginaryUnit(self, expr):
        return '1j'

    def _print_seq(self, seq, delimiter=', '):
        """
        Prints a sequence of items as a string.
        
        This function takes a sequence (list, tuple, etc.) and prints its items as a string, with each item formatted using the `_print` method. Items are separated by a specified delimiter.
        
        Parameters:
        seq (iterable): The sequence of items to be printed.
        delimiter (str, optional): The string used to separate items in the output. Defaults to ','.
        
        Returns:
        str: A string representation of the sequence with items separated
        """

        # simplified _print_seq taken from pretty.py
        s = [self._print(item) for item in seq]
        if s:
            return delimiter.join(s)
        else:
            return ""

    def _print_Function(self, e):
        """
        Print a function in a format suitable for numexpr.
        
        This function takes an expression `e` and returns a string representation of the function in a format that is compatible with numexpr. It handles both standard Python functions and custom implemented functions.
        
        Parameters:
        e (Expression): The expression containing the function to be printed.
        
        Returns:
        str: A string representation of the function in a format suitable for numexpr.
        
        Raises:
        TypeError: If numexpr does not support the function specified in the expression
        """

        func_name = e.func.__name__

        nstr = self._numexpr_functions.get(func_name, None)
        if nstr is None:
            # check for implemented_function
            if hasattr(e, '_imp_'):
                return "(%s)" % self._print(e._imp_(*e.args))
            else:
                raise TypeError("numexpr does not support function '%s'" %
                                func_name)
        return "%s(%s)" % (nstr, self._print_seq(e.args))

    def blacklisted(self, expr):
        raise TypeError("numexpr cannot be used with %s" %
                        expr.__class__.__name__)

    # blacklist all Matrix printing
    _print_SparseMatrix = \
    _print_MutableSparseMatrix = \
    _print_ImmutableSparseMatrix = \
    _print_Matrix = \
    _print_DenseMatrix = \
    _print_MutableDenseMatrix = \
    _print_ImmutableMatrix = \
    _print_ImmutableDenseMatrix = \
    blacklisted
    # blacklist some python expressions
    _print_list = \
    _print_tuple = \
    _print_Tuple = \
    _print_dict = \
    _print_Dict = \
    blacklisted

    def doprint(self, expr):
        lstr = super(NumExprPrinter, self).doprint(expr)
        return "evaluate('%s', truediv=True)" % lstr


for k in NumExprPrinter._numexpr_functions:
    setattr(NumExprPrinter, '_print_%s' % k, NumExprPrinter._print_Function)

def lambdarepr(expr, **settings):
    """
    Returns a string usable for lambdifying.
    """
    return LambdaPrinter(settings).doprint(expr)
