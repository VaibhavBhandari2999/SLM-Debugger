from sympy.printing.dot import (purestr, styleof, attrprint, dotnode,
        dotedges, dotprint)
from sympy import Symbol, Integer, Basic, Expr, srepr
from sympy.abc import x

def test_purestr():
    assert purestr(Symbol('x')) == "Symbol(x)"
    assert purestr(Basic(1, 2)) == "Basic(1, 2)"


def test_styleof():
    styles = [(Basic, {'color': 'blue', 'shape': 'ellipse'}),
              (Expr,  {'color': 'black'})]
    assert styleof(Basic(1), styles) == {'color': 'blue', 'shape': 'ellipse'}

    assert styleof(x + 1, styles) == {'color': 'black', 'shape': 'ellipse'}

def test_attrprint():
    assert attrprint({'color': 'blue', 'shape': 'ellipse'}) == \
           '"color"="blue", "shape"="ellipse"'

def test_dotnode():
    """
    Generate a DOT language node representation for a SymPy expression.
    
    Parameters:
    x (sympy.Expr): The SymPy expression to be represented as a node.
    repeat (bool, optional): If True, append a suffix '_()' to the node label to indicate a repeated node. Default is False.
    
    Returns:
    str: A string representing the DOT language node for the given SymPy expression.
    
    Examples:
    >>> test_dotnode()
    "Symbol(x) ["color"="black", "label"="x
    """


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
    Generate a dot representation of a mathematical expression with a specified depth.
    
    This function takes a mathematical expression and generates a dot representation of the expression's nodes. The depth parameter controls how deep the nodes are included in the representation.
    
    Parameters:
    expr (str or sympy expression): The mathematical expression to be represented.
    depth (int, optional): The depth of the nodes to be included in the dot representation. Default is 0, which means all nodes are included.
    
    Returns:
    str: A
    """

    text = dotprint(3*x+2, depth=1)
    assert dotnode(3*x+2) in text
    assert dotnode(x) not in text
    text = dotprint(3*x+2)
    assert "depth" not in text

def test_Matrix_and_non_basics():
    from sympy import MatrixSymbol
    n = Symbol('n')
    assert dotprint(MatrixSymbol('X', n, n))

def test_labelfunc():
    text = dotprint(x + 2, labelfunc=srepr)
    assert "Symbol('x')" in text
    assert "Integer(2)" in text
