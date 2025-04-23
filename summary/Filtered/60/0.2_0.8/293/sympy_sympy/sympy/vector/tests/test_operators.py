from sympy.vector import CoordSys3D, Gradient, Divergence, Curl, VectorZero, Laplacian
from sympy.printing.repr import srepr

R = CoordSys3D('R')
s1 = R.x*R.y*R.z  # type: ignore
s2 = R.x + 3*R.y**2  # type: ignore
s3 = R.x**2 + R.y**2 + R.z**2  # type: ignore
v1 = R.x*R.i + R.z*R.z*R.j  # type: ignore
v2 = R.x*R.i + R.y*R.j + R.z*R.k  # type: ignore
v3 = R.x**2*R.i + R.y**2*R.j + R.z**2*R.k  # type: ignore


def test_Gradient():
    assert Gradient(s1) == Gradient(R.x*R.y*R.z)
    assert Gradient(s2) == Gradient(R.x + 3*R.y**2)
    assert Gradient(s1).doit() == R.y*R.z*R.i + R.x*R.z*R.j + R.x*R.y*R.k
    assert Gradient(s2).doit() == R.i + 6*R.y*R.j


def test_Divergence():
    """
    Test the Divergence function.
    
    This function checks the correctness of the Divergence function for given vector fields in Cartesian and cylindrical coordinate systems. It verifies the divergence of vector fields and their symbolic evaluation.
    
    Parameters:
    - v1: Vector field in Cartesian coordinates.
    - v2: Vector field in Cartesian coordinates.
    
    Returns:
    - None: The function asserts the correctness of the Divergence function and does not return any value.
    
    Key Points:
    - The function asserts that the divergence of v1 and
    """

    assert Divergence(v1) == Divergence(R.x*R.i + R.z*R.z*R.j)
    assert Divergence(v2) == Divergence(R.x*R.i + R.y*R.j + R.z*R.k)
    assert Divergence(v1).doit() == 1
    assert Divergence(v2).doit() == 3
    # issue 22384
    Rc = CoordSys3D('R', transformation='cylindrical')
    assert Divergence(Rc.i).doit() == 1/Rc.r


def test_Curl():
    """
    Test the Curl function.
    
    This function tests the Curl function with two vector fields v1 and v2. The vectors are defined in terms of the position vector R and its components (x, y, z). The function checks if the computed Curl matches the expected results and if the results are simplified correctly.
    
    Parameters:
    v1 (Vector): A vector field defined as R.x*R.i + R.z*R.z*R.j.
    v2 (Vector): A vector field defined as R.x*R
    """

    assert Curl(v1) == Curl(R.x*R.i + R.z*R.z*R.j)
    assert Curl(v2) == Curl(R.x*R.i + R.y*R.j + R.z*R.k)
    assert Curl(v1).doit() == (-2*R.z)*R.i
    assert Curl(v2).doit() == VectorZero()


def test_Laplacian():
    """
    Compute the Laplacian of a scalar or vector field.
    
    Parameters
    ----------
    s3 : Expr
    A scalar field.
    v3 : Expr
    A vector field.
    
    Returns
    -------
    Expr
    The Laplacian of the input field.
    
    Examples
    --------
    >>> from sympy import symbols, Function, Laplacian
    >>> R, x, y, z = symbols('R x y z')
    >>> s3 = Function('s3')(x, y, z)
    >>> v3
    """

    assert Laplacian(s3) == Laplacian(R.x**2 + R.y**2 + R.z**2)
    assert Laplacian(v3) == Laplacian(R.x**2*R.i + R.y**2*R.j + R.z**2*R.k)
    assert Laplacian(s3).doit() == 6
    assert Laplacian(v3).doit() == 2*R.i + 2*R.j + 2*R.k
    assert srepr(Laplacian(s3)) == \
            'Laplacian(Add(Pow(R.x, Integer(2)), Pow(R.y, Integer(2)), Pow(R.z, Integer(2))))'
