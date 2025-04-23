from sympy.printing.codeprinter import CodePrinter
from sympy.core import symbols
from sympy.core.symbol import Dummy
from sympy.utilities.pytest import raises


def setup_test_printer(**kwargs):
    """
    Generate a CodePrinter instance for testing purposes.
    
    This function creates an instance of the CodePrinter class tailored for testing. The settings for the printer can be customized using keyword arguments. Additionally, a set of unsupported features and a set of symbols to be numbered can be specified.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments to customize the CodePrinter settings.
    
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
    Test the behavior of the `test_print_Symbol` function.
    
    This function tests the printing of symbols using a custom printer. The printer can handle reserved words and can raise errors when encountering them. It also allows for custom suffixes to be added to reserved words.
    
    Parameters:
    - x, y: Symbols to be printed.
    - p: A custom printer object.
    - reserved_words: A set of reserved words that the printer should avoid using in its output.
    - error_on_reserved: A boolean flag
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
