from sympy.printing.codeprinter import CodePrinter
from sympy.printing.str import StrPrinter
from sympy.core import symbols
from sympy.core.symbol import Dummy
from sympy.utilities.pytest import raises


def setup_test_printer(**kwargs):
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
    
    This function tests the printing behavior of symbolic variables using a custom printer. The printer can handle reserved words and can raise errors if a reserved word is encountered. It also allows for custom suffixes to be added to reserved words.
    
    Parameters:
    - x, y: Symbolic variables to be printed.
    - p: A custom printer object.
    - error_on_reserved: A boolean flag to control whether an error should be raised when a reserved word
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

def test_issue_15791():
    assert (CodePrinter._print_MutableSparseMatrix.__name__ ==
    CodePrinter._print_not_supported.__name__)
    assert (CodePrinter._print_ImmutableSparseMatrix.__name__ ==
    CodePrinter._print_not_supported.__name__)
    assert (CodePrinter._print_MutableSparseMatrix.__name__ !=
    StrPrinter._print_MatrixBase.__name__)
    assert (CodePrinter._print_ImmutableSparseMatrix.__name__ !=
    StrPrinter._print_MatrixBase.__name__)
