from sympy.printing.codeprinter import CodePrinter
from sympy.core import symbols
from sympy.core.symbol import Dummy
from sympy.utilities.pytest import raises


def setup_test_printer(**kwargs):
    """
    Generate a CodePrinter instance for testing purposes.
    
    This function creates an instance of the CodePrinter class tailored for testing. The printer's settings are defined by keyword arguments. Additionally, a set of unsupported expressions and a set of symbols to be numbered can be specified.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments that define the settings for the CodePrinter.
    
    Returns:
    CodePrinter: An instance of the CodePrinter class configured for testing.
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
    Test the behavior of the test_print_Symbol function.
    
    This function checks how the test printer handles symbolic variables and reserved words. It creates symbols, uses a custom printer to print these symbols, and tests how reserved words are handled.
    
    Parameters:
    - x, y: Symbolic variables created using sympy's `symbols` function.
    - p: A test printer object created using `setup_test_printer`.
    
    Returns:
    - None: This function does not return any value. It prints the results of the test
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
