from sympy.vector import CoordSys3D, Gradient, Divergence, Curl, VectorZero


R = CoordSys3D('R')
s1 = R.x*R.y*R.z
s2 = R.x + 3*R.y**2
v1 = R.x*R.i + R.z*R.z*R.j
v2 = R.x*R.i + R.y*R.j + R.z*R.k


def test_Gradient():
    assert Gradient(s1) == Gradient(R.x*R.y*R.z)
    assert Gradient(s2) == Gradient(R.x + 3*R.y**2)
    assert Gradient(s1).doit() == R.y*R.z*R.i + R.x*R.z*R.j + R.x*R.y*R.k
    assert Gradient(s2).doit() == R.i + 6*R.y*R.j


def test_Divergence():
    """
    Test the divergence of vector fields.
    
    This function checks the divergence of two vector fields, `v1` and `v2`, in a 3-dimensional space. The vector fields are defined in terms of the position vector `R` with components `x`, `y`, and `z`. The divergence of a vector field is computed using the `Divergence` function.
    
    Parameters:
    - v1: A vector field defined as `R.x*R.i + R.z*R.z*R.j`.
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
 == Curl(R.x*R.i + R.y*R.j + R.z*R.k)
    assert Curl(v1).doit() == (-2*R.z)*R.i
    assert Curl(v2).doit() == VectorZero()
