from sympy import I, Matrix, symbols, conjugate, Expr, Integer

from sympy.physics.quantum.dagger import adjoint, Dagger
from sympy.external import import_module
from sympy.testing.pytest import skip


def test_scalars():
    """
    Tests the behavior of the Dagger function on different types of scalar inputs.
    
    This function checks how the Dagger function processes various scalar inputs, including complex symbols, imaginary numbers, integers, and non-commutative symbols. It ensures that the Dagger function correctly returns the complex conjugate for complex symbols, leaves real numbers unchanged, and maintains the non-commutative property for non-commutative symbols.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - Tests the Dagger function on complex symbols.
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
    """
    Generate the Hermitian conjugate (dagger) of a given matrix.
    
    This function takes a symbolic matrix `m` as input and returns its Hermitian conjugate (also known as the dagger or adjoint).
    
    Parameters:
    m (Matrix): A symbolic matrix with complex entries.
    
    Returns:
    Matrix: The Hermitian conjugate of the input matrix `m`.
    
    Example:
    >>> from sympy import symbols, Matrix, I
    >>> x = symbols('x')
    """

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
    if not np:
        skip("numpy not installed.")

    a = np.matrix([[1.0, 2.0j], [-1.0j, 2.0]])
    adag = a.copy().transpose().conjugate()
    assert (Dagger(a) == adag).all()


scipy = import_module('scipy', import_kwargs={'fromlist': ['sparse']})


def test_scipy_sparse_dagger():
    """
    Test the correctness of the Dagger function for a scipy sparse matrix.
    
    This function checks if the Dagger function correctly computes the Hermitian
    conjugate of a given scipy sparse matrix. The Hermitian conjugate is obtained
    by taking the transpose and the complex conjugate of the matrix.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    - scipy: The scipy library must be installed for this function to work.
    - numpy: The numpy library must be installed for this function
    """

    if not np:
        skip("numpy not installed.")
    if not scipy:
        skip("scipy not installed.")
    else:
        sparse = scipy.sparse

    a = sparse.csr_matrix([[1.0 + 0.0j, 2.0j], [-1.0j, 2.0 + 0.0j]])
    adag = a.copy().transpose().conjugate()
    assert np.linalg.norm((Dagger(a) - adag).todense()) == 0.0
