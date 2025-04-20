from sympy.vector import CoordSys3D, Gradient, Divergence, Curl, VectorZero


R = CoordSys3D('R')
s1 = R.x*R.y*R.z
s2 = R.x + 3*R.y**2
v1 = R.x*R.i + R.z*R.z*R.j
v2 = R.x*R.i + R.y*R.j + R.z*R.k


def test_Gradient():
    """
    Test the Gradient function.
    
    This function checks the correctness of the Gradient function for symbolic expressions involving vectors and scalar fields.
    
    Parameters:
    s1 (str): A string representing a scalar field in terms of vector components.
    s2 (str): A string representing another scalar field in terms of vector components.
    
    Returns:
    bool: True if the Gradient function returns the expected results, False otherwise.
    
    Examples:
    >>> test_Gradient()
    True
    """

    assert Gradient(s1) == Gradient(R.x*R.y*R.z)
    assert Gradient(s2) == Gradient(R.x + 3*R.y**2)
    assert Gradient(s1).doit() == R.y*R.z*R.i + R.x*R.z*R.j + R.x*R.y*R.k
    assert Gradient(s2).doit() == R.i + 6*R.y*R.j


def test_Divergence():
    assert Divergence(v1) == Divergence(R.x*R.i + R.z*R.z*R.j)
    assert Divergence(v2) == Divergence(R.x*R.i + R.y*R.j + R.z*R.k)
    assert Divergence(v1).doit() == 1
    assert Divergence(v2).doit() == 3


def test_Curl():
    """
    Test the Curl function.
    
    This function tests the Curl function with two vector fields v1 and v2. The expected results are provided for each test case.
    
    Parameters:
    v1 (Vector): A vector field defined as R.x*R.i + R.z*R.z*R.j.
    v2 (Vector): A vector field defined as R.x*R.i + R.y*R.j + R.z*R.k.
    
    Returns:
    Vector: The computed curl of the input vector fields.
    """

    assert Curl(v1) == Curl(R.x*R.i + R.z*R.z*R.j)
    assert Curl(v2) == Curl(R.x*R.i + R.y*R.j + R.z*R.k)
    assert Curl(v1).doit() == (-2*R.z)*R.i
    assert Curl(v2).doit() == VectorZero()
