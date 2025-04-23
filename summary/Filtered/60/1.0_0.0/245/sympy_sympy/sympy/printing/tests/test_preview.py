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
    # issue 9107
    a = Symbol('α')
    obj = BytesIO()
    try:
        preview(a, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server


def test_preview_latex_construct_in_expr():
    """
    Generate a preview of a LaTeX expression representing a piecewise function.
    
    This function takes a piecewise function and generates a preview of its LaTeX representation as an image.
    The image is saved in PNG format and stored in a BytesIO buffer.
    
    Parameters:
    pw (Piecewise): The piecewise function to be previewed.
    
    Returns:
    None: The image is saved in a BytesIO buffer and not returned.
    
    Raises:
    RuntimeError: If LaTeX is not installed on the system, the function will catch
    """

    # see PR 9801
    x = Symbol('x')
    pw = Piecewise((1, Eq(x, 0)), (0, True))
    obj = BytesIO()
    try:
        preview(pw, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server
