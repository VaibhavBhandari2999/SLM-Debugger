# -*- coding: utf-8 -*-

from sympy import Symbol, Piecewise, Eq
from sympy.printing.preview import preview

from io import BytesIO


def test_preview():
    x = Symbol('x')
    obj = BytesIO()
    try:
        preview(x, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server


def test_preview_unicode_symbol():
    """
    Generate a PNG preview of a Unicode symbol.
    
    This function creates a PNG preview of a given Unicode symbol and outputs it to a BytesIO object. If the LaTeX package is not installed, a `RuntimeError` will be caught and ignored.
    
    Parameters:
    a (Symbol): The Unicode symbol to preview.
    
    Returns:
    None: The preview is saved in a BytesIO object instead of being displayed.
    
    Raises:
    RuntimeError: If the LaTeX package is not installed and the preview cannot be generated.
    
    Example
    """

    # issue 9107
    a = Symbol('α')
    obj = BytesIO()
    try:
        preview(a, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server


def test_preview_latex_construct_in_expr():
    """
    Generate a preview of a LaTeX construct in an expression.
    
    This function creates a preview of a LaTeX representation of a piecewise
    expression. The function takes a symbolic expression and generates a
    preview in PNG format. The preview is saved to a buffer in memory.
    
    Parameters:
    - pw (Piecewise): The piecewise expression to be previewed.
    
    Returns:
    - None: The preview is saved to a buffer in memory and not returned.
    
    Notes:
    - The function uses the `preview` function from the
    """

    # see PR 9801
    x = Symbol('x')
    pw = Piecewise((1, Eq(x, 0)), (0, True))
    obj = BytesIO()
    try:
        preview(pw, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server
