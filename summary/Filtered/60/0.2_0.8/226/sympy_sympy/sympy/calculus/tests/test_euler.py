from sympy import Symbol, Function, Derivative as D, Eq, cos, sin
from sympy.utilities.pytest import raises
from sympy.calculus.euler import euler_equations as euler


def test_euler_interface():
    """
    Test the Euler interface.
    
    Parameters:
    x (Function): The dependent variable.
    y (Symbol): The independent variable.
    t (Symbol): The independent variable.
    
    Raises:
    TypeError: If the input is not a differential equation or if the dependent variable is not a function.
    ValueError: If the differential equation is not first order.
    TypeError: If the input is not a valid equation.
    
    Returns:
    list: A list of equations derived from the Euler-Lagrange equation.
    """

    x = Function('x')
    y = Symbol('y')
    t = Symbol('t')
    raises(TypeError, lambda: euler())
    raises(TypeError, lambda: euler(D(x(t), t)*y(t), [x(t), y]))
    raises(ValueError, lambda: euler(D(x(t), t)*x(y), [x(t), x(y)]))
    raises(TypeError, lambda: euler(D(x(t), t)**2, x(0)))
    assert euler(D(x(t), t)**2/2, {x(t)}) == [Eq(-D(x(t), t, t))]
    assert euler(D(x(t), t)**2/2, x(t), {t}) == [Eq(-D(x(t), t, t))]


def test_euler_pendulum():
    x = Function('x')
    t = Symbol('t')
    L = D(x(t), t)**2/2 + cos(x(t))
    assert euler(L, x(t), t) == [Eq(-sin(x(t)) - D(x(t), t, t))]


def test_euler_henonheiles():
    x = Function('x')
    y = Function('y')
    t = Symbol('t')
    L = sum(D(z(t), t)**2/2 - z(t)**2/2 for z in [x, y])
    L += -x(t)**2*y(t) + y(t)**3/3
    assert euler(L, [x(t), y(t)], t) == [Eq(-2*x(t)*y(t) - x(t) -
                                            D(x(t), t, t)),
                                         Eq(-x(t)**2 + y(t)**2 -
                                            y(t) - D(y(t), t, t))]


def test_euler_sineg():
    psi = Function('psi')
    t = Symbol('t')
    x = Symbol('x')
    L = D(psi(t, x), t)**2/2 - D(psi(t, x), x)**2/2 + cos(psi(t, x))
    assert euler(L, psi(t, x), [t, x]) == [Eq(-sin(psi(t, x)) -
                                              D(psi(t, x), t, t) +
                                              D(psi(t, x), x, x))]


def test_euler_high_order():
    """
    Test the Euler-Lagrange equations for a given Lagrangian.
    
    This function computes the Euler-Lagrange equations for a given Lagrangian
    with respect to a list of functions and their arguments. The Lagrangian can
    depend on the functions, their first and second derivatives with respect to
    the independent variable, and an optional parameter.
    
    Parameters:
    L (Expr): The Lagrangian, a symbolic expression that depends on the
    functions, their derivatives, and the independent variable
    """

    # an example from hep-th/0309038
    m = Symbol('m')
    k = Symbol('k')
    x = Function('x')
    y = Function('y')
    t = Symbol('t')
    L = (m*D(x(t), t)**2/2 + m*D(y(t), t)**2/2 -
         k*D(x(t), t)*D(y(t), t, t) + k*D(y(t), t)*D(x(t), t, t))
    assert euler(L, [x(t), y(t)]) == [Eq(2*k*D(y(t), t, t, t) -
                                         m*D(x(t), t, t)),
                                      Eq(-2*k*D(x(t), t, t, t) -
                                         m*D(y(t), t, t))]

    w = Symbol('w')
    L = D(x(t, w), t, w)**2/2
    assert euler(L) == [Eq(D(x(t, w), t, t, w, w))]
