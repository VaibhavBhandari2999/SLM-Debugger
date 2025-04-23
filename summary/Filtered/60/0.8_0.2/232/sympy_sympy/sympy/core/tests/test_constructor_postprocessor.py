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
    """
    Postprocesses an expression to remove symbols that do not have the property SymbolRemovesOtherSymbols.
    
    Parameters:
    expr (Expression): The input expression to be postprocessed.
    
    Returns:
    Expression: The postprocessed expression with non-relevant symbols removed.
    
    This function iterates over the arguments of the input expression. If an argument is not a Symbol or is a Symbol that has the property SymbolRemovesOtherSymbols, it is included in the result. The function returns a new expression constructed from the filtered arguments
    """

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
    Construct and test custom postprocessors for symbolic expressions.
    
    This function creates and tests custom postprocessors for symbolic expressions.
    It involves creating symbols and using them in various mathematical operations to
    validate the behavior of the postprocessors.
    
    Parameters:
    None
    
    Returns:
    None
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
