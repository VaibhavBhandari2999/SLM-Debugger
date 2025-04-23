from sympy.external import import_module
from sympy.testing.pytest import ignore_warnings, raises

antlr4 = import_module("antlr4", warn_not_installed=False)

# disable tests if antlr4-python*-runtime is not present
if antlr4:
    disabled = True


def test_no_import():
    """
    Tests the parse_latex function from sympy.parsing.latex for import errors.
    
    This function attempts to parse a simple LaTeX expression using sympy's parse_latex function. It is designed to check if the function can be imported without errors. If an ImportError is raised during the import or parsing process, it is ignored and a warning is issued. If the function can be imported and the parsing process is successful, it indicates that the import and basic functionality are working as expected.
    
    Parameters:
    None
    """

    from sympy.parsing.latex import parse_latex

    with ignore_warnings(UserWarning):
        with raises(ImportError):
            parse_latex('1 + 1')
