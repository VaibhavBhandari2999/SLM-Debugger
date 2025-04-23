from sympy import symbols
from sympy.functions import beta, Ei, zeta, Max, Min, sqrt, exp
from sympy.printing.cxxcode import CXX98CodePrinter, CXX11CodePrinter, CXX17CodePrinter, cxxcode
from sympy.codegen.cfunctions import log1p

x, y = symbols('x y')


def test_CXX98CodePrinter():
    """
    Test the CXX98CodePrinter.
    
    This function checks the behavior of the CXX98CodePrinter for different scenarios:
    - It verifies the printing of a Max function with a single argument.
    - It checks the printing of a Min function with multiple arguments.
    - It asserts the language and standard of the CXX98CodePrinter.
    - It ensures that certain keywords are recognized as reserved words.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Raises:
    - AssertionError: If any of the
    """

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
    class MyPrinter(CXX11CodePrinter):
        def _print_log1p(self, expr):
            return 'my_library::log1p(%s)' % ', '.join(map(self._print, expr.args))

    assert MyPrinter().doprint(log1p(x)) == 'my_library::log1p(x)'


def test_subclass_print_method__ns():
    """
    Prints a C++ expression with a custom namespace.
    
    This function creates a subclass of CXX11CodePrinter that overrides the namespace to prepend 'my_library::' to all printed symbols. It then compares the output of the standard CXX11CodePrinter and the custom MyPrinter for the log1p(x) function.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function demonstrates how to subclass CXX11CodePrinter to customize the namespace.
    - It checks that
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
