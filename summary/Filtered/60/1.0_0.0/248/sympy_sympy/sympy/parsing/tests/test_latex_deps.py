from sympy.external import import_module
from sympy.utilities import pytest


antlr4 = import_module("antlr4")

# disable tests if antlr4-python*-runtime is not present
if antlr4:
    disabled = True


def test_no_import():
    """
    Parse LaTeX code into a SymPy expression.
    
    This function takes a LaTeX string as input and returns the corresponding SymPy expression.
    
    Parameters:
    latex (str): The LaTeX code to be parsed.
    
    Returns:
    sympy.Expr: The SymPy expression corresponding to the input LaTeX code.
    
    Raises:
    ImportError: If the SymPy package is not installed.
    
    Example:
    >>> from sympy.parsing.latex import parse_latex
    >>> parse_latex('1 + 1')
    1 + 1
    """

    from sympy.parsing.latex import parse_latex

    with pytest.raises(ImportError):
        parse_latex('1 + 1')
