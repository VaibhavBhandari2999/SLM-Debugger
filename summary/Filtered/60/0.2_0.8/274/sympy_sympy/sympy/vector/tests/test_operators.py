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
    assert Divergence(v1) == Divergence(R.x*R.i + R.z*R.z*R.j)
    assert Divergence(v2) == Divergence(R.x*R.i + R.y*R.j + R.z*R.k)
    assert Divergence(v1).doit() == 1
    assert Divergence(v2).doit() == 3


def test_Curl():
    """
    Test the Curl function.
    
    This function evaluates the curl of two given vector fields v1 and v2 in a 3D space. The vector fields are defined using the R.x, R.y, and R.z components and the basis vectors R.i, R.j, and R.k. The function checks if the computed curl matches the expected results and if the results are simplified correctly.
    
    Parameters:
    v1 (Vector): The first vector field defined in 3D space.
    v2 (Vector):
    """

    assert Curl(v1) == Curl(R.x*R.i + R.z*R.z*R.j)
    assert Curl(v2) == Curl(R.x*R.i + R.y*R.j + R.z*R.k)
    assert Curl(v1).doit() == (-2*R.z)*R.i
    assert Curl(v2).doit() == VectorZero()


def test_Laplacian():
    assert Laplacian(s3) == Laplacian(R.x**2 + R.y**2 + R.z**2)
    assert Laplacian(v3) == Laplacian(R.x**2*R.i + R.y**2*R.j + R.z**2*R.k)
    assert Laplacian(s3).doit() == 6
    assert Laplacian(v3).doit() == 2*R.i + 2*R.j + 2*R.k
    assert srepr(Laplacian(s3)) == \
            'Laplacian(Add(Pow(R.x, Integer(2)), Pow(R.y, Integer(2)), Pow(R.z, Integer(2))))'
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
