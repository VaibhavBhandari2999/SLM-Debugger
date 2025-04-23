from sympy.printing.codeprinter import CodePrinter
from sympy.core import symbols
from sympy.core.symbol import Dummy
from sympy.utilities.pytest import raises


def setup_test_printer(**kwargs):
    """
    Generate a CodePrinter instance for testing purposes.
    
    This function creates an instance of the CodePrinter class tailored for testing. The printer's settings are defined by keyword arguments. Additionally, a set of unsupported operations and a set of symbols to be numbered can be specified.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments to set the printer's configuration.
    
    Returns:
    CodePrinter: A CodePrinter instance configured for testing.
    """

    p = CodePrinter(settings=kwargs)
    p._not_supported = set()
    p._number_symbols = set()
    return p


def test_print_Dummy():
    d = Dummy('d')
    p = setup_test_printer()
    assert p._print_Dummy(d) == "d_%i" % d.dummy_index

def test_print_Symbol():
    """
    Test the behavior of the `test_print_Symbol` function.
    
    This function tests the `_print` method of a test printer for symbolic expressions. It checks how the printer handles reserved words and how it can be configured to avoid conflicts.
    
    Parameters:
    - x, y: Symbolic variables to be printed.
    - p: A test printer object.
    - error_on_reserved: A boolean flag to control whether an error should be raised when a reserved word is encountered.
    - reserved_word_suffix: A string to
    """


    x, y = symbols('x, if')

    p = setup_test_printer()
    assert p._print(x) == 'x'
    assert p._print(y) == 'if'

    p.reserved_words.update(['if'])
    assert p._print(y) == 'if_'

    p = setup_test_printer(error_on_reserved=True)
    p.reserved_words.update(['if'])
    with raises(ValueError):
        p._print(y)

    p = setup_test_printer(reserved_word_suffix='_He_Man')
    p.reserved_words.update(['if'])
    assert p._print(y) == 'if_He_Man'
