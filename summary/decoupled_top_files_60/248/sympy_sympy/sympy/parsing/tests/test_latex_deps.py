from sympy.external import import_module
from sympy.utilities import pytest


antlr4 = import_module("antlr4")

# disable tests if antlr4-python*-runtime is not present
if antlr4:
    disabled = True


def test_no_import():
    """
    Function to test the absence of import in the parsing of LaTeX expressions.
    
    This function attempts to import and use the `parse_latex` function from the `sympy.parsing.latex` module to parse a simple LaTeX expression. It is expected to raise an `ImportError` because the necessary dependencies might not be available.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ImportError: If the necessary dependencies for parsing LaTeX are not available.
    
    Example:
    ```python
    test_no_import()
    ``
    """

    from sympy.parsing.latex import parse_latex

    with pytest.raises(ImportError):
        parse_latex('1 + 1')
