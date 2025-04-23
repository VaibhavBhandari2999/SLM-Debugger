from sympy.external import import_module
from sympy.utilities import pytest


antlr4 = import_module("antlr4")

# disable tests if antlr4-python*-runtime is not present
if antlr4:
    disabled = True


def test_no_import():
    """
    test_no_import()
    This function tests the parse_latex function from the sympy.parsing.latex module by attempting to import it without the necessary dependencies. It raises an ImportError if the import fails, indicating that the required package is missing.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ImportError: If the sympy.parsing.latex module cannot be imported.
    
    Notes:
    This function is intended to be used for testing purposes to ensure that the parse_latex function raises an ImportError when it should
    """

    from sympy.parsing.latex import parse_latex

    with pytest.raises(ImportError):
        parse_latex('1 + 1')
