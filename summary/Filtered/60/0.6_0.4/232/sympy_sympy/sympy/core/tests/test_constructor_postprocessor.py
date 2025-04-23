from sympy import Symbol, Mul, symbols, Basic


class SymbolInMulOnce(Symbol):
    # Test class for a symbol that can only appear once in a `Mul` expression.
    pass


Basic._constructor_postprocessor_mapping[SymbolInMulOnce] = {
    "Mul": [lambda x: x],
    "Pow": [lambda x: x.base if isinstance(x.base, SymbolInMulOnce) else x],
    "Add": [lambda x: x],
}


def _postprocess_SymbolRemovesOtherSymbols(expr):
    args = tuple(i for i in expr.args if not isinstance(i, Symbol) or isinstance(i, SymbolRemovesOtherSymbols))
    if args == expr.args:
        return expr
    return Mul.fromiter(args)


class SymbolRemovesOtherSymbols(Symbol):
    # Test class for a symbol that removes other symbols in `Mul`.
    pass


Basic._constructor_postprocessor_mapping[SymbolRemovesOtherSymbols] = {
    "Mul": [_postprocess_SymbolRemovesOtherSymbols],
}


def test_constructor_postprocessors1():
    """
    Construct and test postprocessors for symbolic expressions.
    
    This function creates and tests two types of postprocessors for symbolic expressions:
    1. `SymbolInMulOnce`: Ensures that a symbol appears only once in a multiplication.
    2. `SymbolRemovesOtherSymbols`: Removes other symbols from expressions involving a specific symbol.
    
    The function verifies the behavior of these postprocessors through various symbolic expressions and operations.
    
    Parameters:
    - None
    
    Returns:
    - None
    """

    a = symbols("a")
    x = SymbolInMulOnce("x")
    y = SymbolInMulOnce("y")
    assert isinstance(3*x, Mul)
    assert (3*x).args == (3, x)
    assert x*x == x
    assert 3*x*x == 3*x
    assert 2*x*x + x == 3*x
    assert x**3*y*y == x*y
    assert x**5 + y*x**3 == x + x*y

    w = SymbolRemovesOtherSymbols("w")
    assert x*w == w
    assert (3*w).args == (3, w)
    assert 3*a*w**2 == 3*w**2
    assert 3*a*x**3*w**2 == 3*w**2
    assert (w + x).args == (x, w)
