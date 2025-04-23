from sympy.printing.codeprinter import CodePrinter
from sympy.core import symbols
from sympy.core.symbol import Dummy
from sympy.utilities.pytest import raises


def setup_test_printer(**kwargs):
    """
    Generate a CodePrinter instance for testing purposes.
    
    This function sets up a CodePrinter with specific settings for testing. The printer is configured to track unsupported expressions and number symbols.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments representing the settings for the CodePrinter.
    
    Returns:
    CodePrinter: A CodePrinter instance configured for testing.
    """

    p = CodePrinter(settings=kwargs)
    p._not_supported = set()
    p._number_symbols = set()
    return p


def test_print_Dummy():
    """
    Print a Dummy object.
    
    This function takes a Dummy object `d` and a test printer `p` as input. It returns a string representation of the Dummy object, which is formatted as "d_%i" where `%i` is the `dummy_index` attribute of the Dummy object.
    
    Parameters:
    d (Dummy): The Dummy object to be printed.
    p (TestPrinter): The test printer used for formatting the output.
    
    Returns:
    str: The formatted string representation of the Dummy
    """

    d = Dummy('d')
    p = setup_test_printer()
    assert p._print_Dummy(d) == "d_%i" % d.dummy_index

def test_print_Symbol():

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
