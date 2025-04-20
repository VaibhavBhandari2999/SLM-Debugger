from sympy.printing.codeprinter import CodePrinter
from sympy.core import symbols
from sympy.core.symbol import Dummy
from sympy.utilities.pytest import raises


def setup_test_printer(**kwargs):
    """
    Generate a CodePrinter instance for testing purposes.
    
    This function sets up a CodePrinter with specific settings for testing. The printer is configured with a set of not supported operations and a set of number symbols.
    
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
    d = Dummy('d')
    p = setup_test_printer()
    assert p._print_Dummy(d) == "d_%i" % d.dummy_index

def test_print_Symbol():
    """
    Test the behavior of the print_Symbol function with different scenarios.
    
    This function tests the print_Symbol function with various symbols and reserved words. It checks how the function handles reserved words and whether it can handle errors when reserved words are encountered.
    
    Parameters:
    - x, y (Symbol): The symbols to be printed.
    - error_on_reserved (bool, optional): If True, the function will raise an error when a reserved word is encountered. Default is False.
    - reserved_word_suffix (str, optional
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
