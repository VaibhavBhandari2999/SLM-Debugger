from sympy import Symbol, Rational
from sympy.geometry import Circle, Ellipse, Line, Point, Polygon, Ray, RegularPolygon, Segment, Triangle
from sympy.geometry.entity import scale
from sympy.utilities.pytest import raises

from random import random


def test_subs():
    """
    Substitute a symbol or a point with another value in a geometric object.
    
    This function substitutes a symbol or a point with another value in a given geometric object. It supports various geometric objects such as points, segments, rays, lines, triangles, regular polygons, polygons, circles, and ellipses.
    
    Parameters:
    - o: The geometric object in which the substitution is to be performed.
    - x: The symbol or point to be substituted.
    - y: The value to substitute for the symbol or
    """

    x = Symbol('x', real=True)
    y = Symbol('y', real=True)
    p = Point(x, 2)
    q = Point(1, 1)
    r = Point(3, 4)
    for o in [p,
              Segment(p, q),
              Ray(p, q),
              Line(p, q),
              Triangle(p, q, r),
              RegularPolygon(p, 3, 6),
              Polygon(p, q, r, Point(5, 4)),
              Circle(p, 3),
              Ellipse(p, 3, 4)]:
        assert 'y' in str(o.subs(x, y))
    assert p.subs({x: 1}) == Point(1, 2)
    assert Point(1, 2).subs(Point(1, 2), Point(3, 4)) == Point(3, 4)
    assert Point(1, 2).subs((1, 2), Point(3, 4)) == Point(3, 4)
    assert Point(1, 2).subs(Point(1, 2), Point(3, 4)) == Point(3, 4)
    assert Point(1, 2).subs({(1, 2)}) == Point(2, 2)
    raises(ValueError, lambda: Point(1, 2).subs(1))
    raises(ValueError, lambda: Point(1, 1).subs((Point(1, 1), Point(1,
           2)), 1, 2))


def test_transform():
    assert scale(1, 2, (3, 4)).tolist() == \
        [[1, 0, 0], [0, 2, 0], [0, -4, 1]]


def test_reflect_entity_overrides():
    x = Symbol('x', real=True)
    y = Symbol('y', real=True)
    b = Symbol('b')
    m = Symbol('m')
    l = Line((0, b), slope=m)
    p = Point(x, y)
    r = p.reflect(l)
    c = Circle((x, y), 3)
    cr = c.reflect(l)
    assert cr == Circle(r, -3)
    assert c.area == -cr.area

    pent = RegularPolygon((1, 2), 1, 5)
    l = Line(pent.vertices[1],
        slope=Rational(random() - .5, random() - .5))
    rpent = pent.reflect(l)
    assert rpent.center == pent.center.reflect(l)
    rvert = [i.reflect(l) for i in pent.vertices]
    for v in rpent.vertices:
        for i in range(len(rvert)):
            ri = rvert[i]
            if ri.equals(v):
                rvert.remove(ri)
                break
    assert not rvert
    assert pent.area.equals(-rpent.area)
