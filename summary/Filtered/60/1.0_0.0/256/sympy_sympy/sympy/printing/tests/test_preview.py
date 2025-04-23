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
    Generate a PNG preview of the given Unicode symbol.
    
    This function takes a SymPy symbol with a Unicode character and generates a PNG preview of it. The preview is saved to a BytesIO object. If the LaTeX package is not installed, a `RuntimeError` may be raised.
    
    Parameters:
    a (Symbol): The SymPy symbol containing the Unicode character to preview.
    
    Returns:
    None: The preview is saved to a BytesIO object and not returned.
    
    Raises:
    RuntimeError: If the LaTeX
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
