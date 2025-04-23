from sympy import print_gtk, sin
from sympy.utilities.pytest import XFAIL, raises

# this test fails if python-lxml isn't installed. We don't want to depend on
# anything with SymPy


@XFAIL
def test_1():
    """
    Prints the given SymPy expression in a GTK-based viewer.
    
    Parameters:
    expr (sympy.Expr): The SymPy expression to be displayed.
    start_viewer (bool, optional): Whether to start the GTK viewer. Defaults to False.
    
    This function takes a SymPy expression and prints it in a GTK-based viewer. The viewer is started only if the `start_viewer` flag is set to True.
    """

    from sympy.abc import x
    print_gtk(x**2, start_viewer=False)
    print_gtk(x**2 + sin(x)/4, start_viewer=False)


def test_settings():
    from sympy.abc import x
    raises(TypeError, lambda: print_gtk(x, method="garbage"))
