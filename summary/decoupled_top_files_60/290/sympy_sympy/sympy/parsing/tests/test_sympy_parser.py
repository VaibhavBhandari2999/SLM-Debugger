# -*- coding: utf-8 -*-


import sys

from sympy.assumptions import Q
from sympy.core import Symbol, Function, Float, Rational, Integer, I, Mul, Pow, Eq
from sympy.functions import exp, factorial, factorial2, sin
from sympy.logic import And
from sympy.series import Limit
from sympy.testing.pytest import raises, skip

from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, rationalize, TokenError,
    split_symbols, implicit_multiplication, convert_equals_signs,
    convert_xor, function_exponentiation, lambda_notation, auto_symbol,
    repeated_decimals, implicit_multiplication_application,
    auto_number, factorial_notation, implicit_application,
    _transformation, T
    )


def test_sympy_parser():
    x = Symbol('x')
    inputs = {
        '2*x': 2 * x,
        '3.00': Float(3),
        '22/7': Rational(22, 7),
        '2+3j': 2 + 3*I,
        'exp(x)': exp(x),
        'x!': factorial(x),
        'x!!': factorial2(x),
        '(x + 1)! - 1': factorial(x + 1) - 1,
        '3.[3]': Rational(10, 3),
        '.0[3]': Rational(1, 30),
        '3.2[3]': Rational(97, 30),
        '1.3[12]': Rational(433, 330),
        '1 + 3.[3]': Rational(13, 3),
        '1 + .0[3]': Rational(31, 30),
        '1 + 3.2[3]': Rational(127, 30),
        '.[0011]': Rational(1, 909),
        '0.1[00102] + 1': Rational(366697, 333330),
        '1.[0191]': Rational(10190, 9999),
        '10!': 3628800,
        '-(2)': -Integer(2),
        '[-1, -2, 3]': [Integer(-1), Integer(-2), Integer(3)],
        'Symbol("x").free_symbols': x.free_symbols,
        "S('S(3).n(n=3)')": 3.00,
        'factorint(12, visual=True)': Mul(
            Pow(2, 2, evaluate=False),
            Pow(3, 1, evaluate=False),
            evaluate=False),
        'Limit(sin(x), x, 0, dir="-")': Limit(sin(x), x, 0, dir='-'),
        'Q.even(x)': Q.even(x),


    }
    for text, result in inputs.items():
        assert parse_expr(text) == result

    raises(TypeError, lambda:
        parse_expr('x', standard_transformations))
    raises(TypeError, lambda:
        parse_expr('x', transformations=lambda x,y: 1))
    raises(TypeError, lambda:
        parse_expr('x', transformations=(lambda x,y: 1,)))
    raises(TypeError, lambda: parse_expr('x', transformations=((),)))
    raises(TypeError, lambda: parse_expr('x', {}, [], []))
    raises(TypeError, lambda: parse_expr('x', [], [], {}))
    raises(TypeError, lambda: parse_expr('x', [], [], {}))


def test_rationalize():
    """
    Test the rationalization of floating-point numbers.
    
    This function tests the rationalization of floating-point numbers by comparing the parsed result with the expected rational number.
    
    Parameters:
    inputs (dict): A dictionary where the keys are strings representing floating-point numbers and the values are the expected Rational instances.
    
    Returns:
    None: The function asserts that the parsed expression matches the expected result. If any assertion fails, an AssertionError will be raised.
    
    Key Transformations:
    - `standard_transformations`: Standard transformations applied to
    """

    inputs = {
        '0.123': Rational(123, 1000)
    }
    transformations = standard_transformations + (rationalize,)
    for text, result in inputs.items():
        assert parse_expr(text, transformations=transformations) == result


def test_factorial_fail():
    inputs = ['x!!!', 'x!!!!', '(!)']


    for text in inputs:
        try:
            parse_expr(text)
            assert False
        except TokenError:
            assert True


def test_repeated_fail():
    """
    Test function to validate the parsing of floating-point numbers and their usage in indexing operations.
    
    This function tests a series of input strings to ensure that only invalid indexing operations raise exceptions. It checks for valid floating-point numbers and their use in indexing, ensuring that only cases with syntax errors or invalid indexing raise exceptions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    TypeError: If an invalid floating-point number is used in indexing.
    TokenError, SyntaxError: If there is a syntax error
    """

    inputs = ['1[1]', '.1e1[1]', '0x1[1]', '1.1j[1]', '1.1[1 + 1]',
        '0.1[[1]]', '0x1.1[1]']


    # All are valid Python, so only raise TypeError for invalid indexing
    for text in inputs:
        raises(TypeError, lambda: parse_expr(text))


    inputs = ['0.1[', '0.1[1', '0.1[]']
    for text in inputs:
        raises((TokenError, SyntaxError), lambda: parse_expr(text))


def test_repeated_dot_only():
    assert parse_expr('.[1]') == Rational(1, 9)
    assert parse_expr('1 + .[1]') == Rational(10, 9)


def test_local_dict():
    local_dict = {
        'my_function': lambda x: x + 2
    }
    inputs = {
        'my_function(2)': Integer(4)
    }
    for text, result in inputs.items():
        assert parse_expr(text, local_dict=local_dict) == result


def test_local_dict_split_implmult():
    t = standard_transformations + (split_symbols, implicit_multiplication,)
    w = Symbol('w', real=True)
    y = Symbol('y')
    assert parse_expr('yx', local_dict={'x':w}, transformations=t) == y*w


def test_local_dict_symbol_to_fcn():
    """
    Tests if a local dictionary symbol can be correctly converted to a function.
    
    This function checks if a symbolic expression can be parsed using a local dictionary where a symbol is mapped to a function. If the symbol is mapped to a function, the expression should be correctly converted. If the symbol is not mapped to a function, a TypeError should be raised.
    
    Parameters:
    - d (dict): A dictionary where keys are strings and values are either functions or symbols.
    
    Returns:
    - The function corresponding to the key '
    """

    x = Symbol('x')
    d = {'foo': Function('bar')}
    assert parse_expr('foo(x)', local_dict=d) == d['foo'](x)
    d = {'foo': Symbol('baz')}
    raises(TypeError, lambda: parse_expr('foo(x)', local_dict=d))


def test_global_dict():
    global_dict = {
        'Symbol': Symbol
    }
    inputs = {
        'Q & S': And(Symbol('Q'), Symbol('S'))
    }
    for text, result in inputs.items():
        assert parse_expr(text, global_dict=global_dict) == result


def test_issue_2515():
    raises(TokenError, lambda: parse_expr('(()'))
    raises(TokenError, lambda: parse_expr('"""'))


def test_issue_7663():
    x = Symbol('x')
    e = '2*(x+1)'
    assert parse_expr(e, evaluate=0) == parse_expr(e, evaluate=False)
    assert parse_expr(e, evaluate=0).equals(2*(x+1))

def test_recursive_evaluate_false_10560():
    inputs = {
        '4*-3' : '4*-3',
        '-4*3' : '(-4)*3',
        "-2*x*y": '(-2)*x*y',
        "x*-4*x": "x*(-4)*x"
    }
    for text, result in inputs.items():
        assert parse_expr(text, evaluate=False) == parse_expr(result, evaluate=False)


def test_function_evaluate_false():
    inputs = [
        'Abs(0)', 'im(0)', 're(0)', 'sign(0)', 'arg(0)', 'conjugate(0)',
        'acos(0)', 'acot(0)', 'acsc(0)', 'asec(0)', 'asin(0)', 'atan(0)',
        'acosh(0)', 'acoth(0)', 'acsch(0)', 'asech(0)', 'asinh(0)', 'atanh(0)',
        'cos(0)', 'cot(0)', 'csc(0)', 'sec(0)', 'sin(0)', 'tan(0)',
        'cosh(0)', 'coth(0)', 'csch(0)', 'sech(0)', 'sinh(0)', 'tanh(0)',
        'exp(0)', 'log(0)', 'sqrt(0)',
    ]
    for case in inputs:
        expr = parse_expr(case, evaluate=False)
        assert case == str(expr) != str(expr.doit())
    assert str(parse_expr('ln(0)', evaluate=False)) == 'log(0)'
    assert str(parse_expr('cbrt(0)', evaluate=False)) == '0**(1/3)'


def test_issue_10773():
    """
    Test function to check the parsing of mathematical expressions with negative numbers.
    
    Parameters:
    text (str): The input mathematical expression to be parsed.
    result (str): The expected parsed form of the input expression.
    
    This function tests the parsing of mathematical expressions involving negative numbers. It uses SymPy's `parse_expr` function to parse the input expression and the expected result. The function asserts that the parsed input matches the expected parsed result.
    
    Inputs:
    - `text` (str): The mathematical expression to
    """

    inputs = {
    '-10/5': '(-10)/5',
    '-10/-5' : '(-10)/(-5)',
    }
    for text, result in inputs.items():
        assert parse_expr(text, evaluate=False) == parse_expr(result, evaluate=False)


def test_split_symbols():
    transformations = standard_transformations + \
                      (split_symbols, implicit_multiplication,)
    x = Symbol('x')
    y = Symbol('y')
    xy = Symbol('xy')


    assert parse_expr("xy") == xy
    assert parse_expr("xy", transformations=transformations) == x*y


def test_split_symbols_function():
    transformations = standard_transformations + \
                      (split_symbols, implicit_multiplication,)
    x = Symbol('x')
    y = Symbol('y')
    a = Symbol('a')
    f = Function('f')


    assert parse_expr("ay(x+1)", transformations=transformations) == a*y*(x+1)
    assert parse_expr("af(x+1)", transformations=transformations,
                      local_dict={'f':f}) == a*f(x+1)


def test_functional_exponent():
    """
    Parse and transform the input expression to handle exponentiation of trigonometric functions and exponent functions. The function supports raising trigonometric functions to a power and converting exponential expressions to function form. It also handles general base exponentiation with a function.
    
    Parameters:
    - expr (str): The input expression to be parsed and transformed.
    
    Returns:
    - Expr: The transformed expression with exponentiation and exponential functions handled appropriately.
    
    Key Transformations:
    - convert_xor: Converts XOR operations to their equivalent expressions.
    - function
    """

    t = standard_transformations + (convert_xor, function_exponentiation)
    x = Symbol('x')
    y = Symbol('y')
    a = Symbol('a')
    yfcn = Function('y')
    assert parse_expr("sin^2(x)", transformations=t) == (sin(x))**2
    assert parse_expr("sin^y(x)", transformations=t) == (sin(x))**y
    assert parse_expr("exp^y(x)", transformations=t) == (exp(x))**y
    assert parse_expr("E^y(x)", transformations=t) == exp(yfcn(x))
    assert parse_expr("a^y(x)", transformations=t) == a**(yfcn(x))


def test_match_parentheses_implicit_multiplication():
    transformations = standard_transformations + \
                      (implicit_multiplication,)
    raises(TokenError, lambda: parse_expr('(1,2),(3,4]',transformations=transformations))


def test_convert_equals_signs():
    """
    test_convert_equals_signs()
    Converts '=' signs to Eq() in the parsed expression.
    
    Parameters:
    transformations (tuple): A tuple of transformation functions to be applied during parsing.
    
    Returns:
    The parsed expression with '=' signs converted to Eq().
    
    Example usage:
    assert parse_expr("1*2=x", transformations=(convert_equals_signs,)) == Eq(2, x)
    assert parse_expr("y = x", transformations=(convert_equals_signs,)) == Eq(y, x)
    assert parse
    """

    transformations = standard_transformations + \
                        (convert_equals_signs, )
    x = Symbol('x')
    y = Symbol('y')
    assert parse_expr("1*2=x", transformations=transformations) == Eq(2, x)
    assert parse_expr("y = x", transformations=transformations) == Eq(y, x)
    assert parse_expr("(2*y = x) = False",
        transformations=transformations) == Eq(Eq(2*y, x), False)


def test_parse_function_issue_3539():
    x = Symbol('x')
    f = Function('f')
    assert parse_expr('f(x)') == f(x)


def test_split_symbols_numeric():
    """
    Tests the split symbols numeric function with the following parameters:
    - transformations: A list of transformations to be applied during parsing.
    
    The function verifies that the parsing of expressions with numeric symbols and implicit multiplication works correctly. It uses a combination of standard transformations and implicit multiplication application to parse and compare two expressions: '2**n * 3**n' and '2**n3**n', as well as 'n12n34'. The expected result is that the parsed expressions are equivalent to
    """

    transformations = (
        standard_transformations +
        (implicit_multiplication_application,))

    n = Symbol('n')
    expr1 = parse_expr('2**n * 3**n')
    expr2 = parse_expr('2**n3**n', transformations=transformations)
    assert expr1 == expr2 == 2**n*3**n

    expr1 = parse_expr('n12n34', transformations=transformations)
    assert expr1 == n*12*n*34


def test_unicode_names():
    assert parse_expr('α') == Symbol('α')


def test_python3_features():
    # Make sure the tokenizer can handle Python 3-only features
    if sys.version_info < (3, 7):
        skip("test_python3_features requires Python 3.7 or newer")


    assert parse_expr("123_456") == 123456
    assert parse_expr("1.2[3_4]") == parse_expr("1.2[34]") == Rational(611, 495)
    assert parse_expr("1.2[012_012]") == parse_expr("1.2[012012]") == Rational(400, 333)
    assert parse_expr('.[3_4]') == parse_expr('.[34]') == Rational(34, 99)
    assert parse_expr('.1[3_4]') == parse_expr('.1[34]') == Rational(133, 990)
    assert parse_expr('123_123.123_123[3_4]') == parse_expr('123123.123123[34]') == Rational(12189189189211, 99000000)


def test_issue_19501():
    """
    Generate an expression from a string with implicit multiplication.
    
    This function takes a string representing a mathematical expression with
    implicit multiplication and converts it into a SymPy expression. The
    expression is parsed with the given symbol 'x' and a set of transformations
    that include standard transformations and implicit multiplication
    application.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> x = Symbol('x')
    >>> eq = test_issue_19501()
    >>> eq.free_symbols
    """

    x = Symbol('x')
    eq = parse_expr('E**x(1+x)', local_dict={'x': x}, transformations=(
        standard_transformations +
        (implicit_multiplication_application,)))
    assert eq.free_symbols == {x}


def test_parsing_definitions():
    """
    Tests the parsing of mathematical expressions with different transformation settings.
    
    This function checks the parsing of mathematical expressions using various transformation settings. It ensures that the transformations are applied correctly and that the expressions are parsed as expected.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key transformations tested:
    - lambda_notation
    - auto_symbol
    - repeated_decimals
    - auto_number
    - factorial_notation
    - implicit_multiplication_application
    - convert_xor
    - implicit_application
    - implicit_multiplication
    - convert_equals
    """

    from sympy.abc import x
    assert len(_transformation) == 12  # if this changes, extend below
    assert _transformation[0] == lambda_notation
    assert _transformation[1] == auto_symbol
    assert _transformation[2] == repeated_decimals
    assert _transformation[3] == auto_number
    assert _transformation[4] == factorial_notation
    assert _transformation[5] == implicit_multiplication_application
    assert _transformation[6] == convert_xor
    assert _transformation[7] == implicit_application
    assert _transformation[8] == implicit_multiplication
    assert _transformation[9] == convert_equals_signs
    assert _transformation[10] == function_exponentiation
    assert _transformation[11] == rationalize
    assert T[:5] == T[0,1,2,3,4] == standard_transformations
    t = _transformation
    assert T[-1, 0] == (t[len(t) - 1], t[0])
    assert T[:5, 8] == standard_transformations + (t[8],)
    assert parse_expr('0.3x^2', transformations='all') == 3*x**2/10
    assert parse_expr('sin 3x', transformations='implicit') == sin(3*x)


def test_builtins():
    """
    Test built-in Python functions and their equivalent SymPy functions.
    
    This function checks the equivalence of built-in Python functions and their SymPy counterparts. It tests the following functions:
    - abs(x): Returns the absolute value of x.
    - max(x, y): Returns the larger of x and y.
    - min(x, y): Returns the smaller of x and y.
    - pow(x, y): Returns x raised to the power y.
    - pow(x, y, z): Returns x**y %
    """

    cases = [
        ('abs(x)', 'Abs(x)'),
        ('max(x, y)', 'Max(x, y)'),
        ('min(x, y)', 'Min(x, y)'),
        ('pow(x, y)', 'Pow(x, y)'),
    ]
    for built_in_func_call, sympy_func_call in cases:
        assert parse_expr(built_in_func_call) == parse_expr(sympy_func_call)
    assert str(parse_expr('pow(38, -1, 97)')) == '23'
