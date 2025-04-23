from sympy.external import import_module
from sympy.testing.pytest import ignore_warnings, raises

antlr4 = import_module("antlr4", warn_not_installed=False)

# disable tests if antlr4-python*-runtime is not present
if antlr4:
    disabled = True


def test_no_import():
    """
    Test function for checking the import of the parse_latex function from sympy.parsing.latex.
    
    This function attempts to import and use the parse_latex function from the sympy.parsing.latex module. It is designed to verify that the import process raises an ImportError as expected, indicating that the necessary dependencies are not available.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ImportError: If the parse_latex function can be imported successfully, indicating that the required dependencies are not installed.
    
    Notes
    """

    from sympy.parsing.latex import parse_latex

    with ignore_warnings(UserWarning):
        with raises(ImportError):
            parse_latex('1 + 1')
