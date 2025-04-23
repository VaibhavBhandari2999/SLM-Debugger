from sympy.external import import_module
from sympy.testing.pytest import ignore_warnings, raises

antlr4 = import_module("antlr4", warn_not_installed=False)

# disable tests if antlr4-python*-runtime is not present
if antlr4:
    disabled = True


def test_no_import():
    """
    Parse LaTeX string to SymPy expression.
    
    This function takes a LaTeX string as input and returns the corresponding SymPy expression.
    
    Parameters:
    latex_str (str): The LaTeX string to be parsed.
    
    Returns:
    expr (sympy.Expr): The SymPy expression corresponding to the input LaTeX string.
    
    Raises:
    ImportError: If the required dependencies for parsing LaTeX are not available.
    
    Notes:
    This function uses the `sympy.parsing.latex.parse_latex` method to convert the LaTeX
    """

    from sympy.parsing.latex import parse_latex

    with ignore_warnings(UserWarning):
        with raises(ImportError):
            parse_latex('1 + 1')
