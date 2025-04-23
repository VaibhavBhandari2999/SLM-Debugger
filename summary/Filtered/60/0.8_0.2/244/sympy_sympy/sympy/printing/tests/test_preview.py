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
    Generate a PNG preview of a SymPy symbol.
    
    This function creates a PNG preview of a SymPy symbol using the specified output buffer. The symbol is rendered using LaTeX and saved to the provided buffer.
    
    Parameters:
    a (Symbol): The SymPy symbol to preview.
    output (str): The output format for the preview (default is 'png').
    viewer (str): The viewer to use for the output (default is 'BytesIO').
    outputbuffer (BytesIO): The buffer to
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
    Generate a preview of a LaTeX constructed expression.
    
    This function takes a piecewise function and generates a preview of its LaTeX representation.
    The preview is saved in PNG format to a BytesIO object.
    
    Parameters:
    pw (Piecewise): The piecewise function to be previewed.
    
    Returns:
    None: The preview is saved to a BytesIO object and not returned.
    
    Raises:
    RuntimeError: If LaTeX is not installed on the system, the function will catch this exception and pass silently.
    
    Note:
    """

    # see PR 9801
    x = Symbol('x')
    pw = Piecewise((1, Eq(x, 0)), (0, True))
    obj = BytesIO()
    try:
        preview(pw, output='png', viewer='BytesIO', outputbuffer=obj)
    except RuntimeError:
        pass  # latex not installed on CI server
