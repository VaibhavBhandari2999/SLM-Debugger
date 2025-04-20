from sympy import Symbol, Function, Derivative as D, Eq, cos, sin
from sympy.utilities.pytest import raises
from sympy.calculus.euler import euler_equations as euler


def test_euler_interface():
    """
    Test the Euler interface.
    
    This function tests the Euler interface for symbolic mathematics, specifically for the `euler` function. It checks for correct handling of different types of inputs and raises appropriate exceptions for invalid inputs. The function also verifies the correctness of the output for valid inputs.
    
    Parameters:
    - x: A function or symbol representing a mathematical function.
    - y: A symbol representing a variable.
    - t: A symbol representing the independent variable.
    
    Returns:
    - A list of equations or expressions representing the results
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
    Test the Euler-Lagrange equations for a given Lagrangian with multiple functions and higher-order derivatives.
    
    This function computes the Euler-Lagrange equations for a Lagrangian that involves multiple functions and higher-order derivatives. The Lagrangian is provided as a SymPy expression, and the function returns a list of equations representing the Euler-Lagrange equations.
    
    Parameters:
    - L (SymPy expression): The Lagrangian, which is a function of the functions and their derivatives.
    
    Returns:
    -
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
