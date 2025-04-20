from sympy import Symbol, Function, Derivative as D, Eq, cos, sin
from sympy.testing.pytest import raises
from sympy.calculus.euler import euler_equations as euler


def test_euler_interface():
    x = Function('x')
    y = Symbol('y')
    t = Symbol('t')
    raises(TypeError, lambda: euler())
    raises(TypeError, lambda: euler(D(x(t), t)*y(t), [x(t), y]))
    raises(ValueError, lambda: euler(D(x(t), t)*x(y), [x(t), x(y)]))
    raises(TypeError, lambda: euler(D(x(t), t)**2, x(0)))
    raises(TypeError, lambda: euler(D(x(t), t)*y(t), [t]))
    assert euler(D(x(t), t)**2/2, {x(t)}) == [Eq(-D(x(t), t, t), 0)]
    assert euler(D(x(t), t)**2/2, x(t), {t}) == [Eq(-D(x(t), t, t), 0)]


def test_euler_pendulum():
    """
    Test the Euler-Lagrange equation for a simple pendulum.
    
    This function computes the Euler-Lagrange equation for a simple pendulum
    described by the Lagrangian L. The Lagrangian is given by the kinetic
    energy (1/2 * (dx/dt)^2) minus the potential energy (cos(x)).
    
    Parameters:
    None
    
    Returns:
    List[Eq]: A list of equations representing the Euler-Lagrange equation for the pendulum.
    """

    x = Function('x')
    t = Symbol('t')
    L = D(x(t), t)**2/2 + cos(x(t))
    assert euler(L, x(t), t) == [Eq(-sin(x(t)) - D(x(t), t, t), 0)]


def test_euler_henonheiles():
    x = Function('x')
    y = Function('y')
    t = Symbol('t')
    L = sum(D(z(t), t)**2/2 - z(t)**2/2 for z in [x, y])
    L += -x(t)**2*y(t) + y(t)**3/3
    assert euler(L, [x(t), y(t)], t) == [Eq(-2*x(t)*y(t) - x(t) -
                                            D(x(t), t, t), 0),
                                         Eq(-x(t)**2 + y(t)**2 -
                                            y(t) - D(y(t), t, t), 0)]


def test_euler_sineg():
    """
    Test the Euler-Lagrange equation for a sine-Gordon type system.
    
    This function computes the Euler-Lagrange equations for a given Lagrangian
    density that describes a sine-Gordon type system. The Lagrangian density is
    defined as a function of the wave function psi and its derivatives with respect
    to time (t) and space (x).
    
    Parameters:
    psi (Function): The wave function psi(t, x) as a function of time and space.
    t (Symbol
    """

    psi = Function('psi')
    t = Symbol('t')
    x = Symbol('x')
    L = D(psi(t, x), t)**2/2 - D(psi(t, x), x)**2/2 + cos(psi(t, x))
    assert euler(L, psi(t, x), [t, x]) == [Eq(-sin(psi(t, x)) -
                                              D(psi(t, x), t, t) +
                                              D(psi(t, x), x, x), 0)]


def test_euler_high_order():
    # an example from hep-th/0309038
    m = Symbol('m')
    k = Symbol('k')
    x = Function('x')
    y = Function('y')
    t = Symbol('t')
    L = (m*D(x(t), t)**2/2 + m*D(y(t), t)**2/2 -
         k*D(x(t), t)*D(y(t), t, t) + k*D(y(t), t)*D(x(t), t, t))
    assert euler(L, [x(t), y(t)]) == [Eq(2*k*D(y(t), t, t, t) -
                                         m*D(x(t), t, t), 0),
                                      Eq(-2*k*D(x(t), t, t, t) -
                                         m*D(y(t), t, t), 0)]

    w = Symbol('w')
    L = D(x(t, w), t, w)**2/2
    assert euler(L) == [Eq(D(x(t, w), t, t, w, w), 0)]
