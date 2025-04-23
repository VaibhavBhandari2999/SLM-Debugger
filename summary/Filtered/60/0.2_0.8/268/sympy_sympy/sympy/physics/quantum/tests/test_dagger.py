from sympy import I, Matrix, symbols, conjugate, Expr, Integer

from sympy.physics.quantum.dagger import adjoint, Dagger
from sympy.external import import_module
from sympy.testing.pytest import skip


def test_scalars():
    """
    Tests for scalar objects and their dagger (conjugate transpose) operation.
    
    This function checks the behavior of the dagger operation on various scalar types, including complex numbers, integers, and non-commutative symbols. It ensures that the dagger operation correctly handles complex numbers by taking their conjugate, preserves real integers, and respects the non-commutative nature of symbols.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - The function verifies that the dagger operation on a complex symbol 'x
    """

    x = symbols('x', complex=True)
    assert Dagger(x) == conjugate(x)
    assert Dagger(I*x) == -I*conjugate(x)

    i = symbols('i', real=True)
    assert Dagger(i) == i

    p = symbols('p')
    assert isinstance(Dagger(p), adjoint)

    i = Integer(3)
    assert Dagger(i) == i

    A = symbols('A', commutative=False)
    assert Dagger(A).is_commutative is False


def test_matrix():
    x = symbols('x')
    m = Matrix([[I, x*I], [2, 4]])
    assert Dagger(m) == m.H


class Foo(Expr):

    def _eval_adjoint(self):
        return I


def test_eval_adjoint():
    f = Foo()
    d = Dagger(f)
    assert d == I

np = import_module('numpy')


def test_numpy_dagger():
    """
    Test the correct implementation of the dagger operation for a numpy matrix.
    
    This function checks if the numpy package is installed. If not, it skips the test.
    It then creates a 2x2 numpy matrix 'a' and computes its conjugate transpose 'adag'.
    The function verifies if the computed dagger of 'a' using the 'Dagger' function matches 'adag'.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    skip("numpy not installed."): If numpy is not installed.
    """

    if not np:
        skip("numpy not installed.")

    a = np.matrix([[1.0, 2.0j], [-1.0j, 2.0]])
    adag = a.copy().transpose().conjugate()
    assert (Dagger(a) == adag).all()


scipy = import_module('scipy', import_kwargs={'fromlist': ['sparse']})


def test_scipy_sparse_dagger():
    if not np:
        skip("numpy not installed.")
    if not scipy:
        skip("scipy not installed.")
    else:
        sparse = scipy.sparse

    a = sparse.csr_matrix([[1.0 + 0.0j, 2.0j], [-1.0j, 2.0 + 0.0j]])
    adag = a.copy().transpose().conjugate()
    assert np.linalg.norm((Dagger(a) - adag).todense()) == 0.0
