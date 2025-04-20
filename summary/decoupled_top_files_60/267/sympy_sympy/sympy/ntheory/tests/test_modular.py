from sympy.ntheory.modular import crt, crt1, crt2, solve_congruence
from sympy.utilities.pytest import raises


def test_crt():
    """
    Solve the Chinese Remainder Theorem (CRT) problem.
    
    This function checks if a given solution satisfies the CRT problem for a list of moduli and remainders. It also verifies the correctness of the CRT solution using two different methods.
    
    Parameters:
    m (list of int): A list of moduli.
    v (list of int): A list of remainders corresponding to the moduli.
    r (int): The expected solution for the CRT problem.
    symmetric (bool, optional
    """

    def mcrt(m, v, r, symmetric=False):
        """
        Compute the Chinese Remainder Theorem (CRT) for a given set of moduli and remainders.
        
        This function solves the system of congruences defined by the moduli `m` and the corresponding remainders `v`. The solution `r` is returned along with the least common multiple (LCM) of the moduli `mm`.
        
        Parameters:
        m (list of int): A list of pairwise coprime positive integers representing the moduli.
        v (list of int):
        """

        assert crt(m, v, symmetric)[0] == r
        mm, e, s = crt1(m)
        assert crt2(m, v, mm, e, s, symmetric) == (r, mm)

    mcrt([2, 3, 5], [0, 0, 0], 0)
    mcrt([2, 3, 5], [1, 1, 1], 1)

    mcrt([2, 3, 5], [-1, -1, -1], -1, True)
    mcrt([2, 3, 5], [-1, -1, -1], 2*3*5 - 1, False)

    assert crt([656, 350], [811, 133], symmetric=True) == (-56917, 114800)


def test_modular():
    assert solve_congruence(*list(zip([3, 4, 2], [12, 35, 17]))) == (1719, 7140)
    assert solve_congruence(*list(zip([3, 4, 2], [12, 6, 17]))) is None
    assert solve_congruence(*list(zip([3, 4, 2], [13, 7, 17]))) == (172, 1547)
    assert solve_congruence(*list(zip([-10, -3, -15], [13, 7, 17]))) == (172, 1547)
    assert solve_congruence(*list(zip([-10, -3, 1, -15], [13, 7, 7, 17]))) is None
    assert solve_congruence(
        *list(zip([-10, -5, 2, -15], [13, 7, 7, 17]))) == (835, 1547)
    assert solve_congruence(
        *list(zip([-10, -5, 2, -15], [13, 7, 14, 17]))) == (2382, 3094)
    assert solve_congruence(
        *list(zip([-10, 2, 2, -15], [13, 7, 14, 17]))) == (2382, 3094)
    assert solve_congruence(*list(zip((1, 1, 2), (3, 2, 4)))) is None
    raises(
        ValueError, lambda: solve_congruence(*list(zip([3, 4, 2], [12.1, 35, 17]))))
