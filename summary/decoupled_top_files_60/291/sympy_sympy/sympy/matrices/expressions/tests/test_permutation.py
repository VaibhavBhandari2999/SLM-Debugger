from sympy.combinatorics import Permutation
from sympy.core.expr import unchanged
from sympy.matrices import Matrix
from sympy.matrices.expressions import \
    MatMul, BlockDiagMatrix, Determinant, Inverse
from sympy.matrices.expressions.matexpr import MatrixSymbol
from sympy.matrices.expressions.special import ZeroMatrix, OneMatrix, Identity
from sympy.matrices.expressions.permutation import \
    MatrixPermute, PermutationMatrix
from sympy.testing.pytest import raises
from sympy.core.symbol import Symbol


def test_PermutationMatrix_basic():
    """
    Test PermutationMatrix basic functionality.
    
    Parameters
    ----------
    p : Permutation
    Permutation to be converted to a PermutationMatrix.
    
    Returns
    -------
    PermutationMatrix
    PermutationMatrix representation of the input permutation.
    
    Raises
    ------
    ValueError
    If the input permutation is not of the correct length.
    
    Examples
    --------
    >>> p = Permutation([1, 0])
    >>> PermutationMatrix(p)
    Matrix([
    [0, 1],
    [1, 0]])
    >>> isinstance(Per
    """

    p = Permutation([1, 0])
    assert unchanged(PermutationMatrix, p)
    raises(ValueError, lambda: PermutationMatrix((0, 1, 2)))
    assert PermutationMatrix(p).as_explicit() == Matrix([[0, 1], [1, 0]])
    assert isinstance(PermutationMatrix(p)*MatrixSymbol('A', 2, 2), MatMul)


def test_PermutationMatrix_matmul():
    p = Permutation([1, 2, 0])
    P = PermutationMatrix(p)
    M = Matrix([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
    assert (P*M).as_explicit() == P.as_explicit()*M
    assert (M*P).as_explicit() == M*P.as_explicit()

    P1 = PermutationMatrix(Permutation([1, 2, 0]))
    P2 = PermutationMatrix(Permutation([2, 1, 0]))
    P3 = PermutationMatrix(Permutation([1, 0, 2]))
    assert P1*P2 == P3


def test_PermutationMatrix_matpow():
    """
    Test the matrix power operation for a PermutationMatrix.
    
    Parameters:
    p1 (Permutation): The first permutation.
    P1 (PermutationMatrix): The first permutation matrix.
    p2 (Permutation): The second permutation.
    P2 (PermutationMatrix): The second permutation matrix.
    
    Returns:
    None: This function performs an assertion check and does not return any value.
    """

    p1 = Permutation([1, 2, 0])
    P1 = PermutationMatrix(p1)
    p2 = Permutation([2, 0, 1])
    P2 = PermutationMatrix(p2)
    assert P1**2 == P2
    assert P1**3 == Identity(3)


def test_PermutationMatrix_identity():
    """
    Test if a permutation matrix is the identity matrix.
    
    This function checks whether a given permutation matrix corresponds to the identity permutation.
    
    Parameters:
    p (Permutation): A permutation object representing a permutation.
    
    Returns:
    bool: True if the permutation matrix is the identity matrix, False otherwise.
    """

    p = Permutation([0, 1])
    assert PermutationMatrix(p).is_Identity

    p = Permutation([1, 0])
    assert not PermutationMatrix(p).is_Identity


def test_PermutationMatrix_determinant():
    P = PermutationMatrix(Permutation([0, 1, 2]))
    assert Determinant(P).doit() == 1
    P = PermutationMatrix(Permutation([0, 2, 1]))
    assert Determinant(P).doit() == -1
    P = PermutationMatrix(Permutation([2, 0, 1]))
    assert Determinant(P).doit() == 1


def test_PermutationMatrix_inverse():
    P = PermutationMatrix(Permutation(0, 1, 2))
    assert Inverse(P).doit() == PermutationMatrix(Permutation(0, 2, 1))


def test_PermutationMatrix_rewrite_BlockDiagMatrix():
    P = PermutationMatrix(Permutation([0, 1, 2, 3, 4, 5]))
    P0 = PermutationMatrix(Permutation([0]))
    assert P.rewrite(BlockDiagMatrix) == \
        BlockDiagMatrix(P0, P0, P0, P0, P0, P0)

    P = PermutationMatrix(Permutation([0, 1, 3, 2, 4, 5]))
    P10 = PermutationMatrix(Permutation(0, 1))
    assert P.rewrite(BlockDiagMatrix) == \
        BlockDiagMatrix(P0, P0, P10, P0, P0)

    P = PermutationMatrix(Permutation([1, 0, 3, 2, 5, 4]))
    assert P.rewrite(BlockDiagMatrix) == \
        BlockDiagMatrix(P10, P10, P10)

    P = PermutationMatrix(Permutation([0, 4, 3, 2, 1, 5]))
    P3210 = PermutationMatrix(Permutation([3, 2, 1, 0]))
    assert P.rewrite(BlockDiagMatrix) == \
        BlockDiagMatrix(P0, P3210, P0)

    P = PermutationMatrix(Permutation([0, 4, 2, 3, 1, 5]))
    P3120 = PermutationMatrix(Permutation([3, 1, 2, 0]))
    assert P.rewrite(BlockDiagMatrix) == \
        BlockDiagMatrix(P0, P3120, P0)

    P = PermutationMatrix(Permutation(0, 3)(1, 4)(2, 5))
    assert P.rewrite(BlockDiagMatrix) == BlockDiagMatrix(P)


def test_MartrixPermute_basic():
    """
    Test the MatrixPermute function.
    
    Args:
    A (MatrixSymbol): A 2x2 matrix symbol.
    p (Permutation): A permutation object.
    
    Returns:
    MatrixPermute: A matrix permutation object.
    
    Raises:
    ValueError: If the input is not a valid permutation or matrix symbol.
    """

    p = Permutation(0, 1)
    P = PermutationMatrix(p)
    A = MatrixSymbol('A', 2, 2)

    raises(ValueError, lambda: MatrixPermute(Symbol('x'), p))
    raises(ValueError, lambda: MatrixPermute(A, Symbol('x')))

    assert MatrixPermute(A, P) == MatrixPermute(A, p)
    raises(ValueError, lambda: MatrixPermute(A, p, 2))

    pp = Permutation(0, 1, size=3)
    assert MatrixPermute(A, pp) == MatrixPermute(A, p)
    pp = Permutation(0, 1, 2)
    raises(ValueError, lambda: MatrixPermute(A, pp))


def test_MatrixPermute_shape():
    p = Permutation(0, 1)
    A = MatrixSymbol('A', 2, 3)
    assert MatrixPermute(A, p).shape == (2, 3)


def test_MatrixPermute_explicit():
    p = Permutation(0, 1, 2)
    A = MatrixSymbol('A', 3, 3)
    AA = A.as_explicit()
    assert MatrixPermute(A, p, 0).as_explicit() == \
        AA.permute(p, orientation='rows')
    assert MatrixPermute(A, p, 1).as_explicit() == \
        AA.permute(p, orientation='cols')


def test_MatrixPermute_rewrite_MatMul():
    p = Permutation(0, 1, 2)
    A = MatrixSymbol('A', 3, 3)

    assert MatrixPermute(A, p, 0).rewrite(MatMul).as_explicit() == \
        MatrixPermute(A, p, 0).as_explicit()
    assert MatrixPermute(A, p, 1).rewrite(MatMul).as_explicit() == \
        MatrixPermute(A, p, 1).as_explicit()


def test_MatrixPermute_doit():
    """
    Test the MatrixPermute.doit method.
    
    Parameters:
    - p: Permutation object representing the permutation to be applied.
    - A: MatrixSymbol representing the matrix to be permuted.
    - p1, p2: Permutation objects for nested permutations.
    - 0, 1: Dimensions along which the permutation is applied.
    
    This function tests the MatrixPermute.doit method for various scenarios, including:
    - Basic permutation application on a 3x3 matrix.
    - Identity and zero matrices.
    """

    p = Permutation(0, 1, 2)
    A = MatrixSymbol('A', 3, 3)
    assert MatrixPermute(A, p).doit() == MatrixPermute(A, p)

    p = Permutation(0, size=3)
    A = MatrixSymbol('A', 3, 3)
    assert MatrixPermute(A, p).doit().as_explicit() == \
        MatrixPermute(A, p).as_explicit()

    p = Permutation(0, 1, 2)
    A = Identity(3)
    assert MatrixPermute(A, p, 0).doit().as_explicit() == \
        MatrixPermute(A, p, 0).as_explicit()
    assert MatrixPermute(A, p, 1).doit().as_explicit() == \
        MatrixPermute(A, p, 1).as_explicit()

    A = ZeroMatrix(3, 3)
    assert MatrixPermute(A, p).doit() == A
    A = OneMatrix(3, 3)
    assert MatrixPermute(A, p).doit() == A

    A = MatrixSymbol('A', 4, 4)
    p1 = Permutation(0, 1, 2, 3)
    p2 = Permutation(0, 2, 3, 1)
    expr = MatrixPermute(MatrixPermute(A, p1, 0), p2, 0)
    assert expr.as_explicit() == expr.doit().as_explicit()
    expr = MatrixPermute(MatrixPermute(A, p1, 1), p2, 1)
    assert expr.as_explicit() == expr.doit().as_explicit()
t()
.as_explicit()
