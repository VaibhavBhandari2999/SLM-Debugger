from sympy import print_gtk, sin
from sympy.utilities.pytest import XFAIL, raises

# this test fails if python-lxml isn't installed. We don't want to depend on
# anything with SymPy


@XFAIL
def test_1():
    """
    Prints the given SymPy expression in a GTK-friendly format.
    
    Parameters:
    expr (str): The SymPy expression to be printed.
    start_viewer (bool, optional): Whether to start the GTK viewer. Defaults to False.
    
    This function takes a SymPy expression and prints it in a format that is compatible with GTK. It can be used to visualize mathematical expressions in a GTK-based application without starting the viewer by setting the start_viewer parameter to False.
    """

    from sympy.abc import x
    print_gtk(x**2, start_viewer=False)
    print_gtk(x**2 + sin(x)/4, start_viewer=False)


def test_settings():
    from sympy.abc import x
    raises(TypeError, lambda: print_gtk(x, method="garbage"))
