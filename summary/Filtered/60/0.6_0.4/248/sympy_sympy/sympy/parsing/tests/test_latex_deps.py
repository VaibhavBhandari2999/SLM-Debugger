from sympy.external import import_module
from sympy.utilities import pytest


antlr4 = import_module("antlr4")

# disable tests if antlr4-python*-runtime is not present
if antlr4:
    disabled = True


def test_no_import():
    """
    Function to test the parse_latex function from sympy.parsing.latex.
    
    This function attempts to import and use the parse_latex function from sympy.parsing.latex to parse a simple LaTeX expression. It is expected to raise an ImportError due to the absence of necessary dependencies.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ImportError: If the necessary dependencies for sympy.parsing.latex are not available.
    
    Example:
    >>> test_no_import()
    ImportError: ...
    """

    from sympy.parsing.latex import parse_latex

    with pytest.raises(ImportError):
        parse_latex('1 + 1')
