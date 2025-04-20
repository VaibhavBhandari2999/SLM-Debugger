from sympy import var, sturm, subresultants, prem, pquo
from sympy.matrices import Matrix, eye
from sympy.polys.subresultants_qq_zz import (sylvester, bezout,
    subresultants_bezout, modified_subresultants_bezout,
    process_bezout_output, backward_eye,
    sturm_pg, sturm_q, sturm_amv, euclid_pg, euclid_q,
    euclid_amv, modified_subresultants_pg, subresultants_pg,
    subresultants_amv_q, quo_z, rem_z, subresultants_amv,
    modified_subresultants_amv, subresultants_rem,
    subresultants_vv, subresultants_vv_2)


def test_sylvester():
    x = var('x')

    assert sylvester(x**3 -7, 0, x) == sylvester(x**3 -7, 0, x, 1) == Matrix([[0]])
    assert sylvester(0, x**3 -7, x) == sylvester(0, x**3 -7, x, 1) == Matrix([[0]])
    assert sylvester(x**3 -7, 0, x, 2) == Matrix([[0]])
    assert sylvester(0, x**3 -7, x, 2) == Matrix([[0]])

    assert sylvester(x**3 -7, 7, x).det() == sylvester(x**3 -7, 7, x, 1).det() == 343
    assert sylvester(7, x**3 -7, x).det() == sylvester(7, x**3 -7, x, 1).det() == 343
    assert sylvester(x**3 -7, 7, x, 2).det() == -343
    assert sylvester(7, x**3 -7, x, 2).det() == 343

    assert sylvester(3, 7, x).det() == sylvester(3, 7, x, 1).det() == sylvester(3, 7, x, 2).det() == 1

    assert sylvester(3, 0, x).det() == sylvester(3, 0, x, 1).det() == sylvester(3, 0, x, 2).det() == 1

    assert sylvester(x - 3, x - 8, x) == sylvester(x - 3, x - 8, x, 1) == sylvester(x - 3, x - 8, x, 2) == Matrix([[1, -3], [1, -8]])

    assert sylvester(x**3 - 7*x + 7, 3*x**2 - 7, x) == sylvester(x**3 - 7*x + 7, 3*x**2 - 7, x, 1) == Matrix([[1, 0, -7,  7,  0], [0, 1,  0, -7,  7], [3, 0, -7,  0,  0], [0, 3,  0, -7,  0], [0, 0,  3,  0, -7]])

    assert sylvester(x**3 - 7*x + 7, 3*x**2 - 7, x, 2) == Matrix([
[1, 0, -7,  7,  0,  0], [0, 3,  0, -7,  0,  0], [0, 1,  0, -7,  7,  0], [0, 0,  3,  0, -7,  0], [0, 0,  1,  0, -7,  7], [0, 0,  0,  3,  0, -7]])

def test_bezout():
    """
    Generate the Bezout matrix for two polynomials p and q with respect to the variable x.
    
    Parameters:
    p (sympy.polys.polytools.Poly): The first polynomial.
    q (sympy.polys.polytools.Poly): The second polynomial.
    x (sympy.core.symbol.Symbol): The variable with respect to which the Bezout matrix is computed.
    method (str, optional): The method to use for generating the Bezout matrix. Can be 'bz
    """

    x = var('x')

    p = -2*x**5+7*x**3+9*x**2-3*x+1
    q = -10*x**4+21*x**2+18*x-3
    assert bezout(p, q, x, 'bz').det() == sylvester(p, q, x, 2).det()
    assert bezout(p, q, x, 'bz').det() != sylvester(p, q, x, 1).det()
    assert bezout(p, q, x, 'prs') == backward_eye(5) * bezout(p, q, x, 'bz') * backward_eye(5)

def test_subresultants_bezout():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert subresultants_bezout(p, q, x) == subresultants(p, q, x)
    assert subresultants_bezout(p, q, x)[-1] == sylvester(p, q, x).det()
    assert subresultants_bezout(p, q, x) != euclid_amv(p, q, x)
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert subresultants_bezout(p, q, x) == [i*j for i, j in zip(amv_factors, modified_subresultants_amv(p, q, x))]

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert subresultants_bezout(p, q, x) == euclid_amv(p, q, x)

def test_modified_subresultants_bezout():
    """
    Tests the modified subresultants_bezout function.
    
    This function checks the correctness of the modified subresultants_bezout function by comparing its output with the expected results from subresultants_amv, sturm_amv, and sylvester determinant methods. It also verifies that the output is not equal to the sylvester determinant and that it is not the same for the negative of the input polynomial.
    
    Parameters:
    - p (sympy polynomial): The first polynomial input.
    - q
    """

    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert modified_subresultants_bezout(p, q, x) == [i*j for i, j in zip(amv_factors, subresultants_amv(p, q, x))]
    assert modified_subresultants_bezout(p, q, x)[-1] != sylvester(p + x**8, q, x).det()
    assert modified_subresultants_bezout(p, q, x) != sturm_amv(p, q, x)

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert modified_subresultants_bezout(p, q, x) == sturm_amv(p, q, x)
    assert modified_subresultants_bezout(-p, q, x) != sturm_amv(-p, q, x)

def test_sturm_pg():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert sturm_pg(p, q, x)[-1] != sylvester(p, q, x, 2).det()
    sam_factors = [1, 1, -1, -1, 1, 1]
    assert sturm_pg(p, q, x) == [i*j for i,j in zip(sam_factors, euclid_pg(p, q, x))]

    p = -9*x**5 - 5*x**3 - 9
    q = -45*x**4 - 15*x**2
    assert sturm_pg(p, q, x, 1)[-1] == sylvester(p, q, x, 1).det()
    assert sturm_pg(p, q, x)[-1] != sylvester(p, q, x, 2).det()
    assert sturm_pg(-p, q, x)[-1] == sylvester(-p, q, x, 2).det()
    assert sturm_pg(-p, q, x) == modified_subresultants_pg(-p, q, x)

def test_sturm_q():
    x = var('x')

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert sturm_q(p, q, x) == sturm(p)
    assert sturm_q(-p, -q, x) != sturm(-p)


def test_sturm_amv():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert sturm_amv(p, q, x)[-1] != sylvester(p, q, x, 2).det()
    sam_factors = [1, 1, -1, -1, 1, 1]
    assert sturm_amv(p, q, x) == [i*j for i,j in zip(sam_factors, euclid_amv(p, q, x))]

    p = -9*x**5 - 5*x**3 - 9
    q = -45*x**4 - 15*x**2
    assert sturm_amv(p, q, x, 1)[-1] == sylvester(p, q, x, 1).det()
    assert sturm_amv(p, q, x)[-1] != sylvester(p, q, x, 2).det()
    assert sturm_amv(-p, q, x)[-1] == sylvester(-p, q, x, 2).det()
    assert sturm_pg(-p, q, x) == modified_subresultants_pg(-p, q, x)


def test_euclid_pg():
    x = var('x')

    p = x**6+x**5-x**4-x**3+x**2-x+1
    q = 6*x**5+5*x**4-4*x**3-3*x**2+2*x-1
    assert euclid_pg(p, q, x)[-1] == sylvester(p, q, x).det()
    assert euclid_pg(p, q, x) == subresultants_pg(p, q, x)

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert euclid_pg(p, q, x)[-1] != sylvester(p, q, x, 2).det()
    sam_factors = [1, 1, -1, -1, 1, 1]
    assert euclid_pg(p, q, x) == [i*j for i,j in zip(sam_factors, sturm_pg(p, q, x))]


def test_euclid_q():
    """
    Compute the polynomial remainder sequence (PRS) using the Euclidean algorithm and return the last non-zero remainder.
    
    This function calculates the polynomial remainder sequence for two given polynomials using the Euclidean algorithm. The last non-zero remainder in the sequence is returned.
    
    Parameters:
    p (sympy.Poly): The first polynomial in the sequence.
    q (sympy.Poly): The second polynomial in the sequence.
    x (sympy.Symbol): The variable with respect to which the pol
    """

    x = var('x')

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert euclid_q(p, q, x)[-1] == -sturm(p)[-1]


def test_euclid_amv():
    x = var('x')

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert euclid_amv(p, q, x)[-1] == sylvester(p, q, x).det()
    assert euclid_amv(p, q, x) == subresultants_amv(p, q, x)

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert euclid_amv(p, q, x)[-1] != sylvester(p, q, x, 2).det()
    sam_factors = [1, 1, -1, -1, 1, 1]
    assert euclid_amv(p, q, x) == [i*j for i,j in zip(sam_factors, sturm_amv(p, q, x))]


def test_modified_subresultants_pg():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert modified_subresultants_pg(p, q, x) == [i*j for i, j in zip(amv_factors, subresultants_pg(p, q, x))]
    assert modified_subresultants_pg(p, q, x)[-1] != sylvester(p + x**8, q, x).det()
    assert modified_subresultants_pg(p, q, x) != sturm_pg(p, q, x)

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert modified_subresultants_pg(p, q, x) == sturm_pg(p, q, x)
    assert modified_subresultants_pg(-p, q, x) != sturm_pg(-p, q, x)


def test_subresultants_pg():
    """
    Generate subresultant polynomial remainder sequence (PRS) using the polynomial-gcd (PG) method.
    
    This function computes the subresultant polynomial remainder sequence for two polynomials using the polynomial-gcd method. The sequence is a list of polynomials where each polynomial is a subresultant of the previous two polynomials in the sequence. The sequence ends with the determinant of the Sylvester matrix of the input polynomials, which is the greatest common divisor (GCD) of the polynomials.
    
    Parameters
    """

    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert subresultants_pg(p, q, x) == subresultants(p, q, x)
    assert subresultants_pg(p, q, x)[-1] == sylvester(p, q, x).det()
    assert subresultants_pg(p, q, x) != euclid_pg(p, q, x)
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert subresultants_pg(p, q, x) == [i*j for i, j in zip(amv_factors, modified_subresultants_amv(p, q, x))]

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert subresultants_pg(p, q, x) == euclid_pg(p, q, x)


def test_subresultants_amv_q():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert subresultants_amv_q(p, q, x) == subresultants(p, q, x)
    assert subresultants_amv_q(p, q, x)[-1] == sylvester(p, q, x).det()
    assert subresultants_amv_q(p, q, x) != euclid_amv(p, q, x)
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert subresultants_amv_q(p, q, x) == [i*j for i, j in zip(amv_factors, modified_subresultants_amv(p, q, x))]

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert subresultants_amv(p, q, x) == euclid_amv(p, q, x)


def test_rem_z():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert rem_z(p, -q, x) != prem(p, -q, x)

def test_quo_z():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert quo_z(p, -q, x) != pquo(p, -q, x)

def test_subresultants_amv():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert subresultants_amv(p, q, x) == subresultants(p, q, x)
    assert subresultants_amv(p, q, x)[-1] == sylvester(p, q, x).det()
    assert subresultants_amv(p, q, x) != euclid_amv(p, q, x)
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert subresultants_amv(p, q, x) == [i*j for i, j in zip(amv_factors, modified_subresultants_amv(p, q, x))]

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert subresultants_amv(p, q, x) == euclid_amv(p, q, x)


def test_modified_subresultants_amv():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert modified_subresultants_amv(p, q, x) == [i*j for i, j in zip(amv_factors, subresultants_amv(p, q, x))]
    assert modified_subresultants_amv(p, q, x)[-1] != sylvester(p + x**8, q, x).det()
    assert modified_subresultants_amv(p, q, x) != sturm_amv(p, q, x)

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert modified_subresultants_amv(p, q, x) == sturm_amv(p, q, x)
    assert modified_subresultants_amv(-p, q, x) != sturm_amv(-p, q, x)


def test_subresultants_rem():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert subresultants_rem(p, q, x) == subresultants(p, q, x)
    assert subresultants_rem(p, q, x)[-1] == sylvester(p, q, x).det()
    assert subresultants_rem(p, q, x) != euclid_amv(p, q, x)
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert subresultants_rem(p, q, x) == [i*j for i, j in zip(amv_factors, modified_subresultants_amv(p, q, x))]

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert subresultants_rem(p, q, x) == euclid_amv(p, q, x)


def test_subresultants_vv():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert subresultants_vv(p, q, x) == subresultants(p, q, x)
    assert subresultants_vv(p, q, x)[-1] == sylvester(p, q, x).det()
    assert subresultants_vv(p, q, x) != euclid_amv(p, q, x)
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert subresultants_vv(p, q, x) == [i*j for i, j in zip(amv_factors, modified_subresultants_amv(p, q, x))]

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert subresultants_vv(p, q, x) == euclid_amv(p, q, x)


def test_subresultants_vv_2():
    x = var('x')

    p = x**8 + x**6 - 3*x**4 - 3*x**3 + 8*x**2 + 2*x - 5
    q = 3*x**6 + 5*x**4 - 4*x**2 - 9*x + 21
    assert subresultants_vv_2(p, q, x) == subresultants(p, q, x)
    assert subresultants_vv_2(p, q, x)[-1] == sylvester(p, q, x).det()
    assert subresultants_vv_2(p, q, x) != euclid_amv(p, q, x)
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert subresultants_vv_2(p, q, x) == [i*j for i, j in zip(amv_factors, modified_subresultants_amv(p, q, x))]

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert subresultants_vv_2(p, q, x) == euclid_amv(p, q, x)
5*x**4 - 4*x**2 - 9*x + 21
    assert subresultants_vv_2(p, q, x) == subresultants(p, q, x)
    assert subresultants_vv_2(p, q, x)[-1] == sylvester(p, q, x).det()
    assert subresultants_vv_2(p, q, x) != euclid_amv(p, q, x)
    amv_factors = [1, 1, -1, 1, -1, 1]
    assert subresultants_vv_2(p, q, x) == [i*j for i, j in zip(amv_factors, modified_subresultants_amv(p, q, x))]

    p = x**3 - 7*x + 7
    q = 3*x**2 - 7
    assert subresultants_vv_2(p, q, x) == euclid_amv(p, q, x)
