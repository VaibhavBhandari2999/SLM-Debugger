from sympy.printing.codeprinter import CodePrinter
from sympy.core import symbols
from sympy.core.symbol import Dummy
from sympy.utilities.pytest import raises


def setup_test_printer(**kwargs):
    p = CodePrinter(settings=kwargs)
    p._not_supported = set()
    p._number_symbols = set()
    return p


def test_print_Dummy():
    """
    Print a Dummy object.
    
    This function takes a Dummy object and a test printer as input. It returns a string representation of the Dummy object, formatted as "d_%i", where %i is the dummy_index attribute of the Dummy object.
    
    Parameters:
    d (Dummy): The Dummy object to be printed.
    p (TestPrinter): The test printer used for formatting.
    
    Returns:
    str: The formatted string representation of the Dummy object.
    """

    d = Dummy('d')
    p = setup_test_printer()
    assert p._print_Dummy(d) == "d_%i" % d.dummy_index

def test_print_Symbol():
    """
    Test the behavior of the `test_print_Symbol` function.
    
    This function tests the `_print` method of a `setup_test_printer` object for printing symbols. It checks how symbols are printed when no reserved words are present, how symbols are renamed when a reserved word is encountered, and how errors are handled when reserved words are used. It also tests the suffix added to reserved words.
    
    Parameters:
    - x, y: Symbols to be printed.
    - p: A `setup_test_printer` object
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
