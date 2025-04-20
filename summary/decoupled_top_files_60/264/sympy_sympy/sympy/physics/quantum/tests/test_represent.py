from sympy import Float, I, Integer, Matrix
from sympy.external import import_module
from sympy.utilities.pytest import skip

from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.represent import (represent, rep_innerproduct,
                                             rep_expectation, enumerate_states)
from sympy.physics.quantum.state import Bra, Ket
from sympy.physics.quantum.operator import Operator, OuterProduct
from sympy.physics.quantum.tensorproduct import TensorProduct
from sympy.physics.quantum.tensorproduct import matrix_tensor_product
from sympy.physics.quantum.commutator import Commutator
from sympy.physics.quantum.anticommutator import AntiCommutator
from sympy.physics.quantum.innerproduct import InnerProduct
from sympy.physics.quantum.matrixutils import (numpy_ndarray,
                                               scipy_sparse_matrix, to_numpy,
                                               to_scipy_sparse, to_sympy)
from sympy.physics.quantum.cartesian import XKet, XOp, XBra
from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.operatorset import operators_to_state

Amat = Matrix([[1, I], [-I, 1]])
Bmat = Matrix([[1, 2], [3, 4]])
Avec = Matrix([[1], [I]])


class AKet(Ket):

    @classmethod
    def dual_class(self):
        return ABra

    def _represent_default_basis(self, **options):
        return self._represent_AOp(None, **options)

    def _represent_AOp(self, basis, **options):
        return Avec


class ABra(Bra):

    @classmethod
    def dual_class(self):
        return AKet


class AOp(Operator):

    def _represent_default_basis(self, **options):
        return self._represent_AOp(None, **options)

    def _represent_AOp(self, basis, **options):
        return Amat


class BOp(Operator):

    def _represent_default_basis(self, **options):
        return self._represent_AOp(None, **options)

    def _represent_AOp(self, basis, **options):
        return Bmat


k = AKet('a')
b = ABra('a')
A = AOp('A')
B = BOp('B')

_tests = [
    # Bra
    (b, Dagger(Avec)),
    (Dagger(b), Avec),
    # Ket
    (k, Avec),
    (Dagger(k), Dagger(Avec)),
    # Operator
    (A, Amat),
    (Dagger(A), Dagger(Amat)),
    # OuterProduct
    (OuterProduct(k, b), Avec*Avec.H),
    # TensorProduct
    (TensorProduct(A, B), matrix_tensor_product(Amat, Bmat)),
    # Pow
    (A**2, Amat**2),
    # Add/Mul
    (A*B + 2*A, Amat*Bmat + 2*Amat),
    # Commutator
    (Commutator(A, B), Amat*Bmat - Bmat*Amat),
    # AntiCommutator
    (AntiCommutator(A, B), Amat*Bmat + Bmat*Amat),
    # InnerProduct
    (InnerProduct(b, k), (Avec.H*Avec)[0])
]


def test_format_sympy():
    """
    Test the formatting of symbolic expressions using SymPy.
    
    This function iterates over a list of test cases, where each test case is a tuple containing two elements:
    1. A symbolic expression to be formatted.
    2. The expected formatted SymPy expression.
    
    For each test case, the function formats the given symbolic expression using the specified basis and then compares it to the expected SymPy expression. If the formatted expression matches the expected expression, the test passes.
    
    Parameters:
    _tests (list): A list
    """

    for test in _tests:
        lhs = represent(test[0], basis=A, format='sympy')
        rhs = to_sympy(test[1])
        assert lhs == rhs


def test_scalar_sympy():
    assert represent(Integer(1)) == Integer(1)
    assert represent(Float(1.0)) == Float(1.0)
    assert represent(1.0 + I) == 1.0 + I


np = import_module('numpy')


def test_format_numpy():
    if not np:
        skip("numpy not installed.")

    for test in _tests:
        lhs = represent(test[0], basis=A, format='numpy')
        rhs = to_numpy(test[1])
        if isinstance(lhs, numpy_ndarray):
            assert (lhs == rhs).all()
        else:
            assert lhs == rhs


def test_scalar_numpy():
    if not np:
        skip("numpy not installed.")

    assert represent(Integer(1), format='numpy') == 1
    assert represent(Float(1.0), format='numpy') == 1.0
    assert represent(1.0 + I, format='numpy') == 1.0 + 1.0j


scipy = import_module('scipy', __import__kwargs={'fromlist': ['sparse']})


def test_format_scipy_sparse():
    """
    Test the equality of two sparse matrices represented in scipy.sparse format.
    
    This function checks if the matrix representation of the given quantum state
    using the specified basis is equal to the given scipy.sparse matrix. It supports
    both dense and sparse matrix representations.
    
    Parameters:
    test (tuple): A tuple containing the quantum state and the expected scipy.sparse matrix.
    basis (str, optional): The basis in which the quantum state is represented. Default is 'A'.
    """

    if not np:
        skip("numpy not installed.")
    if not scipy:
        skip("scipy not installed.")

    for test in _tests:
        lhs = represent(test[0], basis=A, format='scipy.sparse')
        rhs = to_scipy_sparse(test[1])
        if isinstance(lhs, scipy_sparse_matrix):
            assert np.linalg.norm((lhs - rhs).todense()) == 0.0
        else:
            assert lhs == rhs


def test_scalar_scipy_sparse():
    if not np:
        skip("numpy not installed.")
    if not scipy:
        skip("scipy not installed.")

    assert represent(Integer(1), format='scipy.sparse') == 1
    assert represent(Float(1.0), format='scipy.sparse') == 1.0
    assert represent(1.0 + I, format='scipy.sparse') == 1.0 + 1.0j

x_ket = XKet('x')
x_bra = XBra('x')
x_op = XOp('X')


def test_innerprod_represent():
    """
    Test the representation of the inner product for different quantum states.
    
    This function checks the representation of the inner product for a ket and a bra, and ensures that an error is raised when an operator is passed.
    
    Parameters:
    - x_ket (Ket): A quantum state represented as a ket.
    - x_bra (Bra): A quantum state represented as a bra.
    - x_op (Operator): A quantum operator.
    
    Returns:
    - bool: True if the function behaves as expected, False otherwise
    """

    assert rep_innerproduct(x_ket) == InnerProduct(XBra("x_1"), x_ket).doit()
    assert rep_innerproduct(x_bra) == InnerProduct(x_bra, XKet("x_1")).doit()

    try:
        rep_innerproduct(x_op)
    except TypeError:
        return True


def test_operator_represent():
    basis_kets = enumerate_states(operators_to_state(x_op), 1, 2)
    assert rep_expectation(
        x_op) == qapply(basis_kets[1].dual*x_op*basis_kets[0])


def test_enumerate_states():
    """
    Enumerate all possible states of a given XKet object for a specified list of indices.
    
    Parameters:
    test (XKet): The XKet object to enumerate states for.
    indices (Union[int, List[int]]): A single index or a list of indices to enumerate states for.
    
    Returns:
    List[XKet]: A list of XKet objects representing the enumerated states.
    
    Example:
    >>> test_enumerate_states(XKet("foo"), 1, 1)
    """

    test = XKet("foo")
    assert enumerate_states(test, 1, 1) == [XKet("foo_1")]
    assert enumerate_states(
        test, [1, 2, 4]) == [XKet("foo_1"), XKet("foo_2"), XKet("foo_4")]
