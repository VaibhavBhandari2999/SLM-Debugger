# -*- coding: utf-8 -*-

from sympy import Symbol, Piecewise, Eq
from sympy.printing.preview import preview

from io import BytesIO


def test_preview():
    """
    Generate a PNG preview of the given SymPy expression.
    
    This function creates a PNG image of the specified SymPy expression and writes it to a BytesIO object. If the LaTeX package is not installed, a `RuntimeError` may be raised.
    
    Parameters:
    x (sympy.Expr): The SymPy expression to be previewed.
    
    Returns:
    None: The image is written to a BytesIO object, which can be used to save or display the image.
    
    Raises:
    RuntimeError: If
    """

    x = Symbol('x')
    obj = BytesIO()
    try:
        preview(x, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server


def test_preview_unicode_symbol():
    # issue 9107
    a = Symbol('α')
    obj = BytesIO()
    try:
        preview(a, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server


def test_preview_latex_construct_in_expr():
    """
    Generate a preview of a LaTeX construct within an expression.
    
    This function creates a preview of a LaTeX representation of a piecewise
    function. The piecewise function is defined using SymPy's `Piecewise` class.
    The preview is generated in PNG format and stored in a BytesIO object.
    
    Parameters:
    x (Symbol): The symbol used in the piecewise function.
    
    Returns:
    None: The function does not return a value. Instead, it writes the
    preview to a BytesIO object
    """

    # see PR 9801
    x = Symbol('x')
    pw = Piecewise((1, Eq(x, 0)), (0, True))
    obj = BytesIO()
    try:
        preview(pw, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server
