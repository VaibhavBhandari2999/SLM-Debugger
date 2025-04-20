# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from sympy.codegen import Assignment
from sympy.core import Expr, Mod, symbols, Eq, Le, Gt, zoo, oo, Rational
from sympy.core.numbers import pi
from sympy.codegen.ast import none
from sympy.external import import_module
from sympy.logic import And, Or
from sympy.functions import acos, Piecewise, sign
from sympy.matrices import SparseMatrix
from sympy.printing.pycode import (
    MpmathPrinter, NumPyPrinter, PythonCodePrinter, pycode, SciPyPrinter
)
from sympy.utilities.pytest import raises

x, y, z = symbols('x y z')


def test_PythonCodePrinter():
    """
    Tests the PythonCodePrinter.
    
    The function initializes a PythonCodePrinter, checks for module imports, and tests the printing of various expressions and functions. It verifies the output for basic operations, modulus, logical operations, mathematical constants, trigonometric functions, assignment, and piecewise functions. The function also ensures that the correct modules are imported when necessary.
    
    Parameters:
    - None
    
    Returns:
    - None
    """

    prntr = PythonCodePrinter()
    assert not prntr.module_imports
    assert prntr.doprint(x**y) == 'x**y'
    assert prntr.doprint(Mod(x, 2)) == 'x % 2'
    assert prntr.doprint(And(x, y)) == 'x and y'
    assert prntr.doprint(Or(x, y)) == 'x or y'
    assert not prntr.module_imports
    assert prntr.doprint(pi) == 'math.pi'
    assert prntr.module_imports == {'math': {'pi'}}
    assert prntr.doprint(acos(x)) == 'math.acos(x)'
    assert prntr.doprint(Assignment(x, 2)) == 'x = 2'
    assert prntr.doprint(Piecewise((1, Eq(x, 0)),
                        (2, x>6))) == '((1) if (x == 0) else (2) if (x > 6) else None)'
    assert prntr.doprint(Piecewise((2, Le(x, 0)),
                        (3, Gt(x, 0)), evaluate=False)) == '((2) if (x <= 0) else'\
                                                        ' (3) if (x > 0) else None)'
    assert prntr.doprint(sign(x)) == '(0.0 if x == 0 else math.copysign(1, x))'


def test_MpmathPrinter():
    """
    Test the MpmathPrinter.
    
    Args:
    None
    
    Returns:
    None
    
    This function tests the MpmathPrinter by checking the output for specific inputs. It verifies that the sign function is correctly printed with 'mpmath.sign(x)' and that a Rational number is correctly converted to a division of mpf numbers.
    """

    p = MpmathPrinter()
    assert p.doprint(sign(x)) == 'mpmath.sign(x)'
    assert p.doprint(Rational(1, 2)) == 'mpmath.mpf(1)/mpmath.mpf(2)'

def test_NumPyPrinter():
    p = NumPyPrinter()
    assert p.doprint(sign(x)) == 'numpy.sign(x)'


def test_SciPyPrinter():
    p = SciPyPrinter()
    expr = acos(x)
    assert 'numpy' not in p.module_imports
    assert p.doprint(expr) == 'numpy.arccos(x)'
    assert 'numpy' in p.module_imports
    assert not any(m.startswith('scipy') for m in p.module_imports)
    smat = SparseMatrix(2, 5, {(0, 1): 3})
    assert p.doprint(smat) == 'scipy.sparse.coo_matrix([3], ([0], [1]), shape=(2, 5))'
    assert 'scipy.sparse' in p.module_imports


def test_pycode_reserved_words():
    """
    Generate Python code from a SymPy expression, handling reserved words.
    
    This function takes a SymPy expression and converts it into a valid Python
    code string. If `error_on_reserved` is set to `True`, it will raise a ValueError
    if the expression contains Python reserved words. Otherwise, it will replace
    these words with an underscore suffix.
    
    Parameters:
    expr (sympy.Expr): The SymPy expression to be converted.
    error_on_reserved (bool, optional): If True,
    """

    s1, s2 = symbols('if else')
    raises(ValueError, lambda: pycode(s1 + s2, error_on_reserved=True))
    py_str = pycode(s1 + s2)
    assert py_str in ('else_ + if_', 'if_ + else_')


class CustomPrintedObject(Expr):
    def _numpycode(self, printer):
        return 'numpy'

    def _mpmathcode(self, printer):
        return 'mpmath'


def test_printmethod():
    obj = CustomPrintedObject()
    assert NumPyPrinter().doprint(obj) == 'numpy'
    assert MpmathPrinter().doprint(obj) == 'mpmath'


def test_codegen_ast_nodes():
    assert pycode(none) == 'None'


def test_issue_14283():
    """
    Function to test handling of special values in PythonCodePrinter.
    
    This function uses the PythonCodePrinter to convert SymPy objects to their
    equivalent Python representations. It specifically checks the conversion of
    two special values, `zoo` (complex infinity) and `-oo` (negative infinity),
    to their Python equivalents.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses `PythonCodePrinter` to convert SymPy objects to Python.
    - It verifies that
    """

    prntr = PythonCodePrinter()

    assert prntr.doprint(zoo) == "float('nan')"
    assert prntr.doprint(-oo) == "float('-inf')"
