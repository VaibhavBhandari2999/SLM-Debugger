from sympy.printing.dot import (purestr, styleof, attrprint, dotnode,
        dotedges, dotprint)
from sympy import Symbol, Integer, Basic, Expr, srepr
from sympy.abc import x

def test_purestr():
    assert purestr(Symbol('x')) == "Symbol(x)"
    assert purestr(Basic(1, 2)) == "Basic(1, 2)"


def test_styleof():
    """
    Generate a style dictionary based on the given object and a list of style definitions.
    
    Parameters:
    styles (list of tuples): A list where each tuple contains a class and a dictionary of style attributes.
    
    Returns:
    dict: A dictionary representing the style attributes of the given object.
    
    Example:
    styles = [(Basic, {'color': 'blue', 'shape': 'ellipse'}),
    (Expr,  {'color': 'black'})]
    assert styleof(Basic(1), styles) == {'color': '
    """

    styles = [(Basic, {'color': 'blue', 'shape': 'ellipse'}),
              (Expr,  {'color': 'black'})]
    assert styleof(Basic(1), styles) == {'color': 'blue', 'shape': 'ellipse'}

    assert styleof(x + 1, styles) == {'color': 'black', 'shape': 'ellipse'}

def test_attrprint():
    assert attrprint({'color': 'blue', 'shape': 'ellipse'}) == \
           '"color"="blue", "shape"="ellipse"'

def test_dotnode():

    assert dotnode(x, repeat=False) ==\
            '"Symbol(x)" ["color"="black", "label"="x", "shape"="ellipse"];'
    assert dotnode(x+2, repeat=False) == \
            '"Add(Integer(2), Symbol(x))" ["color"="black", "label"="Add", "shape"="ellipse"];'

    assert dotnode(x + x**2, repeat=False) == \
        '"Add(Symbol(x), Pow(Symbol(x), Integer(2)))" ["color"="black", "label"="Add", "shape"="ellipse"];'
    assert dotnode(x + x**2, repeat=True) == \
        '"Add(Symbol(x), Pow(Symbol(x), Integer(2)))_()" ["color"="black", "label"="Add", "shape"="ellipse"];'

def test_dotedges():
    assert sorted(dotedges(x+2, repeat=False)) == [
        '"Add(Integer(2), Symbol(x))" -> "Integer(2)";',
        '"Add(Integer(2), Symbol(x))" -> "Symbol(x)";'
        ]
    assert sorted(dotedges(x + 2, repeat=True)) == [
        '"Add(Integer(2), Symbol(x))_()" -> "Integer(2)_(0,)";',
        '"Add(Integer(2), Symbol(x))_()" -> "Symbol(x)_(1,)";'
    ]

def test_dotprint():
    text = dotprint(x+2, repeat=False)
    assert all(e in text for e in dotedges(x+2, repeat=False))
    assert all(n in text for n in [dotnode(expr, repeat=False) for expr in (x, Integer(2), x+2)])
    assert 'digraph' in text
    text = dotprint(x+x**2, repeat=False)
    assert all(e in text for e in dotedges(x+x**2, repeat=False))
    assert all(n in text for n in [dotnode(expr, repeat=False) for expr in (x, Integer(2), x**2)])
    assert 'digraph' in text
    text = dotprint(x+x**2, repeat=True)
    assert all(e in text for e in dotedges(x+x**2, repeat=True))
    assert all(n in text for n in [dotnode(expr, pos=()) for expr in [x + x**2]])
    text = dotprint(x**x, repeat=True)
    assert all(e in text for e in dotedges(x**x, repeat=True))
    assert all(n in text for n in [dotnode(x, pos=(0,)), dotnode(x, pos=(1,))])
    assert 'digraph' in text

def test_dotprint_depth():
    """
    Test the dotprint function with a specified depth.
    
    This function evaluates the dotprint function on the expression 3*x + 2 with a depth of 1. It checks if the dotnode representation of the expression 3*x+2 is present in the output and ensures that the dotnode representation of x is not present.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Parameters:
    - depth (int): The depth to which the expression should be printed in the dot representation.
    
    Keywords:
    """

    text = dotprint(3*x+2, depth=1)
    assert dotnode(3*x+2) in text
    assert dotnode(x) not in text

def test_Matrix_and_non_basics():
    from sympy import MatrixSymbol
    n = Symbol('n')
    assert dotprint(MatrixSymbol('X', n, n))

def test_labelfunc():
    text = dotprint(x + 2, labelfunc=srepr)
    assert "Symbol('x')" in text
    assert "Integer(2)" in text
labelfunc=srepr)
    assert "Symbol('x')" in text
    assert "Integer(2)" in text
