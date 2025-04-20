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
    """
    Test the Gradient function.
    
    This function checks the correctness of the Gradient function for symbolic expressions involving vectors and scalar fields.
    
    Parameters:
    s1 (str): A string representing a scalar field in terms of vector components (e.g., 'x*y*z').
    s2 (str): A string representing another scalar field in terms of vector components (e.g., 'x + 3*y**2').
    
    Returns:
    None: The function asserts the correctness of the Gradient function and does not return
    """

    assert Gradient(s1) == Gradient(R.x*R.y*R.z)
    assert Gradient(s2) == Gradient(R.x + 3*R.y**2)
    assert Gradient(s1).doit() == R.y*R.z*R.i + R.x*R.z*R.j + R.x*R.y*R.k
    assert Gradient(s2).doit() == R.i + 6*R.y*R.j


def test_Divergence():
    """
    Test the divergence of vector fields.
    
    This function checks the divergence of two vector fields, `v1` and `v2`, in a 3D space defined by the coordinates (x, y, z). The vector fields are represented using the `R` object, which is assumed to be a vector basis in the Cartesian coordinate system.
    
    Parameters:
    v1 (Vector): The first vector field defined as R.x*R.i + R.z*R.z*R.j.
    v2 (Vector
    """

    assert Divergence(v1) == Divergence(R.x*R.i + R.z*R.z*R.j)
    assert Divergence(v2) == Divergence(R.x*R.i + R.y*R.j + R.z*R.k)
    assert Divergence(v1).doit() == 1
    assert Divergence(v2).doit() == 3


def test_Curl():
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
Integer(2)), Pow(R.y, Integer(2)), Pow(R.z, Integer(2))))'
