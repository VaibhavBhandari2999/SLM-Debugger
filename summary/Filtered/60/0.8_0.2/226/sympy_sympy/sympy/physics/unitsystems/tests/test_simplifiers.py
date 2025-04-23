# -*- coding: utf-8 -*-

from __future__ import division

from sympy import Add, Pow, Mul, sin

from sympy.physics.unitsystems.simplifiers import dim_simplify, qsimplify
from sympy.physics.unitsystems.quantities import Quantity as Q
from sympy.physics.unitsystems.systems import mks, mks_dim

L, T = mks_dim["length"], mks_dim["time"]


def test_dim_simplify_add():
    assert dim_simplify(Add(L, L)) == L
    assert dim_simplify(L + L) == L


def test_dim_simplify_mul():
    assert dim_simplify(Mul(L, T)) == L.mul(T)
    assert dim_simplify(L * T) == L.mul(T)


def test_dim_simplify_pow():
    assert dim_simplify(Pow(L, 2)) == L.pow(2)
    assert dim_simplify(L**2) == L.pow(2)


def test_dim_simplify_rec():
    assert dim_simplify(Mul(Add(L, L), T)) == L.mul(T)
    assert dim_simplify((L + L) * T) == L.mul(T)


def test_dim_simplify_dimless():
    assert dim_simplify(Mul(Pow(sin(Mul(L, Pow(L,-1))), 2),L)) == L
    assert dim_simplify(sin(L * L**(-1))**2 * L) == L


m, s = mks["m"], mks["s"]

q1 = Q(10, m)
q2 = Q(5, m)


def test_qsimplify_add():
    assert qsimplify(Add(q1, q2)) == q1.add(q2)


def test_qsimplify_mul():
    """
    Test the qsimplify function for multiplication of Quantum objects.
    
    This function checks the qsimplify function to ensure it correctly simplifies the multiplication of Quantum objects.
    
    Parameters:
    q1 (Quantum): The first Quantum object to be multiplied.
    q2 (Quantum): The second Quantum object to be multiplied.
    q3 (Quantum): The third Quantum object to be multiplied.
    
    Returns:
    Quantum: The simplified result of the multiplication of the Quantum objects.
    
    Key Points:
    - The function
    """

    q3 = Q(2, s)

    assert qsimplify(Mul(q1, q2)) == q1.mul(q2)
    assert qsimplify(Mul(q1, q3)) == q1.mul(q3)


def test_qsimplify_pow():
    assert qsimplify(Pow(q1, 2)) == q1.pow(2)


def test_qsimplify_rec():
    """
    Test the qsimplify function for simplifying a multiplication of a sum with a quantum object.
    
    This function checks if the qsimplify function correctly simplifies the expression of multiplying a sum of two quantum objects (q1 and q2) by another quantum object (q3).
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - q1: First quantum object.
    - q2: Second quantum object.
    - q3: Third quantum object, which is a quantum object with
    """

    q3 = Q(2, s)

    assert qsimplify(Mul(Add(q1, q2), q3)) == q1.add(q2).mul(q3)
