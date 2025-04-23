from sympy.holonomic.recurrence import RecurrenceOperators, RecurrenceOperator
from sympy import symbols, ZZ, QQ


def test_RecurrenceOperator():
    """
    Test the RecurrenceOperator functionality.
    
    This function tests the RecurrenceOperator by performing several operations on symbolic expressions involving the operator Sn and the variable n. It verifies that the operator behaves as expected under multiplication and composition.
    
    Parameters:
    - n (Symbol): The symbolic variable used in the expressions.
    
    Returns:
    - None: The function asserts the correctness of the RecurrenceOperator through equality checks.
    
    Key Operations:
    1. Sn * n == (n + 1) * Sn
    2. Sn * n
    """

    n = symbols('n', integer=True)
    R, Sn = RecurrenceOperators(QQ.old_poly_ring(n), 'Sn')
    assert Sn*n == (n + 1)*Sn
    assert Sn*n**2 == (n**2+1+2*n)*Sn
    assert Sn**2*n**2 == (n**2 + 4*n + 4)*Sn**2
    p = (Sn**3*n**2 + Sn*n)**2
    q = (n**2 + 3*n + 2)*Sn**2 + (2*n**3 + 19*n**2 + 57*n + 52)*Sn**4 + (n**4 + 18*n**3 + \
        117*n**2 + 324*n + 324)*Sn**6
    assert p == q
