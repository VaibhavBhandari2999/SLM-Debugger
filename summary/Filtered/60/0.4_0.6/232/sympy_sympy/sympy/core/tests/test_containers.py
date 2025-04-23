from collections import defaultdict
from sympy import Matrix, Tuple, symbols, sympify, Basic, Dict, S, FiniteSet, Integer
from sympy.core.containers import tuple_wrapper
from sympy.utilities.pytest import raises
from sympy.core.compatibility import is_sequence, iterable, range


def test_Tuple():
    t = (1, 2, 3, 4)
    st = Tuple(*t)
    assert set(sympify(t)) == set(st)
    assert len(t) == len(st)
    assert set(sympify(t[:2])) == set(st[:2])
    assert isinstance(st[:], Tuple)
    assert st == Tuple(1, 2, 3, 4)
    assert st.func(*st.args) == st
    p, q, r, s = symbols('p q r s')
    t2 = (p, q, r, s)
    st2 = Tuple(*t2)
    assert st2.atoms() == set(t2)
    assert st == st2.subs({p: 1, q: 2, r: 3, s: 4})
    # issue 5505
    assert all(isinstance(arg, Basic) for arg in st.args)
    assert Tuple(p, 1).subs(p, 0) == Tuple(0, 1)
    assert Tuple(p, Tuple(p, 1)).subs(p, 0) == Tuple(0, Tuple(0, 1))

    assert Tuple(t2) == Tuple(Tuple(*t2))
    assert Tuple.fromiter(t2) == Tuple(*t2)
    assert Tuple.fromiter(x for x in range(4)) == Tuple(0, 1, 2, 3)
    assert st2.fromiter(st2.args) == st2


def test_Tuple_contains():
    """
    Test if a tuple (t1) is contained within another tuple (t2).
    
    Parameters:
    t1 (Tuple): The first tuple to check for containment.
    t2 (Tuple): The second tuple, which may contain the first tuple.
    
    Returns:
    bool: True if t1 is found within t2, False otherwise.
    
    Example:
    >>> t1, t2 = Tuple(1), Tuple(2)
    >>> test_Tuple_contains()
    True
    >>> t2
    """

    t1, t2 = Tuple(1), Tuple(2)
    assert t1 in Tuple(1, 2, 3, t1, Tuple(t2))
    assert t2 not in Tuple(1, 2, 3, t1, Tuple(t2))


def test_Tuple_concatenation():
    assert Tuple(1, 2) + Tuple(3, 4) == Tuple(1, 2, 3, 4)
    assert (1, 2) + Tuple(3, 4) == Tuple(1, 2, 3, 4)
    assert Tuple(1, 2) + (3, 4) == Tuple(1, 2, 3, 4)
    raises(TypeError, lambda: Tuple(1, 2) + 3)
    raises(TypeError, lambda: 1 + Tuple(2, 3))

    #the Tuple case in __radd__ is only reached when a subclass is involved
    class Tuple2(Tuple):
        def __radd__(self, other):
            return Tuple.__radd__(self, other + other)
    assert Tuple(1, 2) + Tuple2(3, 4) == Tuple(1, 2, 1, 2, 3, 4)
    assert Tuple2(1, 2) + Tuple(3, 4) == Tuple(1, 2, 3, 4)


def test_Tuple_equality():
    assert Tuple(1, 2) is not (1, 2)
    assert (Tuple(1, 2) == (1, 2)) is True
    assert (Tuple(1, 2) != (1, 2)) is False
    assert (Tuple(1, 2) == (1, 3)) is False
    assert (Tuple(1, 2) != (1, 3)) is True
    assert (Tuple(1, 2) == Tuple(1, 2)) is True
    assert (Tuple(1, 2) != Tuple(1, 2)) is False
    assert (Tuple(1, 2) == Tuple(1, 3)) is False
    assert (Tuple(1, 2) != Tuple(1, 3)) is True


def test_Tuple_comparision():
    assert (Tuple(1, 3) >= Tuple(-10, 30)) is S.true
    assert (Tuple(1, 3) <= Tuple(-10, 30)) is S.false
    assert (Tuple(1, 3) >= Tuple(1, 3)) is S.true
    assert (Tuple(1, 3) <= Tuple(1, 3)) is S.true


def test_Tuple_tuple_count():
    assert Tuple(0, 1, 2, 3).tuple_count(4) == 0
    assert Tuple(0, 4, 1, 2, 3).tuple_count(4) == 1
    assert Tuple(0, 4, 1, 4, 2, 3).tuple_count(4) == 2
    assert Tuple(0, 4, 1, 4, 2, 4, 3).tuple_count(4) == 3


def test_Tuple_index():
    """
    Test the index method for a Tuple object.
    
    Parameters:
    Tuple (tuple): A tuple containing integer elements.
    value (int): The value to search for within the tuple.
    
    Returns:
    int: The index of the first occurrence of the value within the tuple, or raises ValueError if the value is not found.
    
    Raises:
    ValueError: If the value is not found in the tuple, or if the optional start and stop parameters are used incorrectly.
    
    Examples:
    >>> test_Tuple_index()
    """

    assert Tuple(4, 0, 1, 2, 3).index(4) == 0
    assert Tuple(0, 4, 1, 2, 3).index(4) == 1
    assert Tuple(0, 1, 4, 2, 3).index(4) == 2
    assert Tuple(0, 1, 2, 4, 3).index(4) == 3
    assert Tuple(0, 1, 2, 3, 4).index(4) == 4

    raises(ValueError, lambda: Tuple(0, 1, 2, 3).index(4))
    raises(ValueError, lambda: Tuple(4, 0, 1, 2, 3).index(4, 1))
    raises(ValueError, lambda: Tuple(0, 1, 2, 3, 4).index(4, 1, 4))


def test_Tuple_mul():
    """
    Test the multiplication of a tuple with an integer.
    
    - `Tuple(1, 2, 3) * 2` should return `Tuple(1, 2, 3, 1, 2, 3)`.
    - `2 * Tuple(1, 2, 3)` should return `Tuple(1, 2, 3, 1, 2, 3)`.
    - `Tuple(1, 2, 3) * Integer
    """

    assert Tuple(1, 2, 3)*2 == Tuple(1, 2, 3, 1, 2, 3)
    assert 2*Tuple(1, 2, 3) == Tuple(1, 2, 3, 1, 2, 3)
    assert Tuple(1, 2, 3)*Integer(2) == Tuple(1, 2, 3, 1, 2, 3)
    assert Integer(2)*Tuple(1, 2, 3) == Tuple(1, 2, 3, 1, 2, 3)

    raises(TypeError, lambda: Tuple(1, 2, 3)*S.Half)
    raises(TypeError, lambda: S.Half*Tuple(1, 2, 3))


def test_tuple_wrapper():
    """
    Wrapper function for converting arguments to tuples.
    
    This function takes any number of positional arguments and converts each argument that is not already a tuple into a tuple. It then returns the arguments as a tuple.
    
    Parameters:
    *t: Variable length argument list. Each argument can be any type, but non-tuple arguments will be converted to tuples.
    
    Returns:
    A tuple containing the arguments, with non-tuple arguments converted to tuples.
    """


    @tuple_wrapper
    def wrap_tuples_and_return(*t):
        return t

    p = symbols('p')
    assert wrap_tuples_and_return(p, 1) == (p, 1)
    assert wrap_tuples_and_return((p, 1)) == (Tuple(p, 1),)
    assert wrap_tuples_and_return(1, (p, 2), 3) == (1, Tuple(p, 2), 3)


def test_iterable_is_sequence():
    ordered = [list(), tuple(), Tuple(), Matrix([[]])]
    unordered = [set()]
    not_sympy_iterable = [{}, '', u'']
    assert all(is_sequence(i) for i in ordered)
    assert all(not is_sequence(i) for i in unordered)
    assert all(iterable(i) for i in ordered + unordered)
    assert all(not iterable(i) for i in not_sympy_iterable)
    assert all(iterable(i, exclude=None) for i in not_sympy_iterable)


def test_Dict():
    x, y, z = symbols('x y z')
    d = Dict({x: 1, y: 2, z: 3})
    assert d[x] == 1
    assert d[y] == 2
    raises(KeyError, lambda: d[2])
    assert len(d) == 3
    assert set(d.keys()) == set((x, y, z))
    assert set(d.values()) == set((S(1), S(2), S(3)))
    assert d.get(5, 'default') == 'default'
    assert x in d and z in d and not 5 in d
    assert d.has(x) and d.has(1)  # SymPy Basic .has method

    # Test input types
    # input - a python dict
    # input - items as args - SymPy style
    assert (Dict({x: 1, y: 2, z: 3}) ==
            Dict((x, 1), (y, 2), (z, 3)))

    raises(TypeError, lambda: Dict(((x, 1), (y, 2), (z, 3))))
    with raises(NotImplementedError):
        d[5] = 6  # assert immutability

    assert set(
        d.items()) == set((Tuple(x, S(1)), Tuple(y, S(2)), Tuple(z, S(3))))
    assert set(d) == {x, y, z}
    assert str(d) == '{x: 1, y: 2, z: 3}'
    assert d.__repr__() == '{x: 1, y: 2, z: 3}'

    # Test creating a Dict from a Dict.
    d = Dict({x: 1, y: 2, z: 3})
    assert d == Dict(d)

    # Test for supporting defaultdict
    d = defaultdict(int)
    assert d[x] == 0
    assert d[y] == 0
    assert d[z] == 0
    assert Dict(d)
    d = Dict(d)
    assert len(d) == 3
    assert set(d.keys()) == set((x, y, z))
    assert set(d.values()) == set((S(0), S(0), S(0)))


def test_issue_5788():
    args = [(1, 2), (2, 1)]
    for o in [Dict, Tuple, FiniteSet]:
        # __eq__ and arg handling
        if o != Tuple:
            assert o(*args) == o(*reversed(args))
        pair = [o(*args), o(*reversed(args))]
        assert sorted(pair) == sorted(reversed(pair))
        assert set(o(*args))  # doesn't fail
