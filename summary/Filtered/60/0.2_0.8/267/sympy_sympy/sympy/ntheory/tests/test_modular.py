from sympy.ntheory.modular import crt, crt1, crt2, solve_congruence
from sympy.utilities.pytest import raises


def test_crt():
    """
    Solve the Chinese Remainder Theorem (CRT) problem.
    
    This function checks if the solution to the CRT problem matches the expected result `r` given the moduli `m` and the respective remainders `v`. It also verifies the correctness of the solution using an alternative method.
    
    Parameters:
    m (list): A list of moduli.
    v (list): A list of remainders corresponding to the moduli.
    r (int): The expected result of the CRT problem.
    """

    def mcrt(m, v, r, symmetric=False):
        """
        Computes the solution to a system of congruences using the Chinese Remainder Theorem (CRT).
        
        Parameters:
        m (list): A list of positive integers representing the moduli.
        v (list): A list of integers representing the remainders corresponding to each modulus in `m`.
        symmetric (bool, optional): If True, uses a symmetric version of the CRT algorithm. Default is False.
        
        Returns:
        int: The unique solution to the system of congruences modulo the product
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
    """
    Solve a system of linear congruences using the Chinese Remainder Theorem.
    
    This function takes a list of tuples, where each tuple contains a coefficient and a remainder, representing a linear congruence equation. It returns the smallest non-negative solution and the modulus if the system has a solution, or None if the system is inconsistent.
    
    Parameters:
    congruences (list of tuples): A list of tuples, where each tuple contains a coefficient and a remainder for a linear congruence equation
    """

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
