from sympy.external import import_module
from sympy.testing.pytest import ignore_warnings, raises

antlr4 = import_module("antlr4", warn_not_installed=False)

# disable tests if antlr4-python*-runtime is not present
if antlr4:
    disabled = True


def test_no_import():
    """
    Parse LaTeX into SymPy expressions.
    
    This function takes a LaTeX string and converts it into a SymPy expression.
    It raises an ImportError if the required dependencies are not available.
    
    Parameters:
    latex_str (str): The LaTeX string to be parsed.
    
    Returns:
    sympy.Expr: The SymPy expression corresponding to the input LaTeX string.
    
    Raises:
    ImportError: If the required dependencies are not available.
    UserWarning: If there are any issues with parsing the LaTeX string.
    """

    from sympy.parsing.latex import parse_latex

    with ignore_warnings(UserWarning):
        with raises(ImportError):
            parse_latex('1 + 1')
