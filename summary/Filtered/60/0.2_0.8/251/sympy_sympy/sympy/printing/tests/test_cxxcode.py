from sympy import symbols
from sympy.functions import beta, Ei, zeta, Max, Min, sqrt, exp
from sympy.printing.cxxcode import CXX98CodePrinter, CXX11CodePrinter, CXX17CodePrinter, cxxcode
from sympy.codegen.cfunctions import log1p

x, y = symbols('x y')


def test_CXX98CodePrinter():
    assert CXX98CodePrinter().doprint(Max(x, 3)) in ('std::max(x, 3)', 'std::max(3, x)')
    assert CXX98CodePrinter().doprint(Min(x, 3, sqrt(x))) == 'std::min(3, std::min(x, std::sqrt(x)))'
    cxx98printer = CXX98CodePrinter()
    assert cxx98printer.language == 'C++'
    assert cxx98printer.standard == 'C++98'
    assert 'template' in cxx98printer.reserved_words
    assert 'alignas' not in cxx98printer.reserved_words


def test_CXX11CodePrinter():
    assert CXX11CodePrinter().doprint(log1p(x)) == 'std::log1p(x)'

    cxx11printer = CXX11CodePrinter()
    assert cxx11printer.language == 'C++'
    assert cxx11printer.standard == 'C++11'
    assert 'operator' in cxx11printer.reserved_words
    assert 'noexcept' in cxx11printer.reserved_words
    assert 'concept' not in cxx11printer.reserved_words


def test_subclass_print_method():
    """
    Tests the custom print method for a subclass of CXX11CodePrinter.
    
    This function creates a subclass of CXX11CodePrinter and overrides the _print_log1p method to customize the printing of log1p expressions. The test checks if the custom print method correctly formats the log1p expression using the specified library function.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Methods:
    - _print_log1p: Custom print method for log1p expressions.
    
    Example:
    """

    class MyPrinter(CXX11CodePrinter):
        def _print_log1p(self, expr):
            return 'my_library::log1p(%s)' % ', '.join(map(self._print, expr.args))

    assert MyPrinter().doprint(log1p(x)) == 'my_library::log1p(x)'


def test_subclass_print_method__ns():
    """
    Generate a custom C++ code printer that adds a namespace prefix to the output.
    
    This function creates a subclass of CXX11CodePrinter that overrides the namespace
    prefix to include 'my_library::'. The printer is then used to print a C++ expression
    with the specified namespace prefix.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example usage:
    p = CXX11CodePrinter()
    myp = MyPrinter()
    print(p.doprint(log1p(x)))
    """

    class MyPrinter(CXX11CodePrinter):
        _ns = 'my_library::'

    p = CXX11CodePrinter()
    myp = MyPrinter()

    assert p.doprint(log1p(x)) == 'std::log1p(x)'
    assert myp.doprint(log1p(x)) == 'my_library::log1p(x)'


def test_CXX17CodePrinter():
    assert CXX17CodePrinter().doprint(beta(x, y)) == 'std::beta(x, y)'
    assert CXX17CodePrinter().doprint(Ei(x)) == 'std::expint(x)'
    assert CXX17CodePrinter().doprint(zeta(x)) == 'std::riemann_zeta(x)'


def test_cxxcode():
    assert sorted(cxxcode(sqrt(x)*.5).split('*')) == sorted(['0.5', 'std::sqrt(x)'])
