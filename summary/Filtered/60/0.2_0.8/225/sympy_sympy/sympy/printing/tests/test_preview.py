# -*- coding: utf-8 -*-

from sympy import Symbol, Piecewise, Eq
from sympy.printing.preview import preview

from io import BytesIO


def test_preview():
    """
    Generate a PNG preview of the given SymPy expression.
    
    This function creates a PNG image of the specified SymPy expression and saves it to a BytesIO buffer. If the LaTeX package is not installed, a `RuntimeError` may be raised.
    
    Parameters:
    x (sympy.Expr): The SymPy expression to be previewed.
    
    Returns:
    bytes: The PNG image data of the expression.
    
    Raises:
    RuntimeError: If the LaTeX package is not installed and the preview cannot be generated.
    """

    x = Symbol('x')
    obj = BytesIO()
    try:
        preview(x, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server


def test_preview_unicode_symbol():
    """
    Generate a PNG preview of a Unicode symbol.
    
    This function creates a PNG preview of a given Unicode symbol and saves it to a BytesIO object. If the LaTeX package is not installed, a `RuntimeError` may be raised.
    
    Parameters:
    a (Symbol): The Unicode symbol to preview.
    
    Returns:
    None: The preview is saved to a BytesIO object and not returned.
    
    Raises:
    RuntimeError: If the LaTeX package is not installed and the preview cannot be generated.
    """

    # issue 9107
    a = Symbol('α')
    obj = BytesIO()
    try:
        preview(a, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server


def test_preview_latex_construct_in_expr():
    # see PR 9801
    x = Symbol('x')
    pw = Piecewise((1, Eq(x, 0)), (0, True))
    obj = BytesIO()
    try:
        preview(pw, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server
