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
    Tests the MpmathPrinter function.
    
    This function checks the MpmathPrinter's ability to convert SymPy expressions into Mpmath-compatible strings. It specifically tests the conversion of the sign function and Rational numbers.
    
    Parameters:
    None
    
    Returns:
    None
    """

    p = MpmathPrinter()
    assert p.doprint(sign(x)) == 'mpmath.sign(x)'
    assert p.doprint(Rational(1, 2)) == 'mpmath.mpf(1)/mpmath.mpf(2)'

def test_NumPyPrinter():
    p = NumPyPrinter()
    assert p.doprint(sign(x)) == 'numpy.sign(x)'


def test_SciPyPrinter():
    """
    Tests the functionality of the SciPyPrinter.
    
    This function creates an instance of the SciPyPrinter and tests its ability to handle expressions and matrix types. It checks if the necessary modules are imported and if the correct string representations are generated for the given expressions and matrices.
    
    Parameters:
    None
    
    Returns:
    None
    """

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
    """
    Prints the representation of a CustomPrintedObject using different printers.
    
    This function takes a CustomPrintedObject and prints its representation using either the NumPyPrinter or the MpmathPrinter. It asserts that the printed output matches the expected string for each printer.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The printed output using NumPyPrinter should be 'numpy'.
    - The printed output using MpmathPrinter should be 'mpmath'.
    """

    obj = CustomPrintedObject()
    assert NumPyPrinter().doprint(obj) == 'numpy'
    assert MpmathPrinter().doprint(obj) == 'mpmath'


def test_codegen_ast_nodes():
    assert pycode(none) == 'None'


def test_issue_14283():
    prntr = PythonCodePrinter()

    assert prntr.doprint(zoo) == "float('nan')"
    assert prntr.doprint(-oo) == "float('-inf')"
