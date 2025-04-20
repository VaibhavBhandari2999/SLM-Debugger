from __future__ import print_function, division

from re import match
from sympy import sympify


def mathematica(s):
    return sympify(parse(s))


def parse(s):
    """
    Parse a mathematical expression string into a simplified form.
    
    This function takes a string representing a mathematical expression and
    parses it according to a set of predefined rules. The rules cover various
    arithmetic operations, function calls, and implied multiplications. The
    function returns a simplified string representation of the expression.
    
    Parameters:
    s (str): The input string representing the mathematical expression.
    
    Returns:
    str: A simplified string representation of the input expression.
    
    Rules:
    1. Arithmetic operation between a constant and
    """

    s = s.strip()

    # Begin rules
    rules = (
        # Arithmetic operation between a constant and a function
        (r"\A(\d+)([*/+-^])(\w+\[[^\]]+[^\[]*\])\Z",
        lambda m: m.group(
            1) + translateFunction(m.group(2)) + parse(m.group(3))),

        # Arithmetic operation between two functions
        (r"\A(\w+\[[^\]]+[^\[]*\])([*/+-^])(\w+\[[^\]]+[^\[]*\])\Z",
        lambda m: parse(m.group(1)) + translateFunction(
            m.group(2)) + parse(m.group(3))),

        (r"\A(\w+)\[([^\]]+[^\[]*)\]\Z",  # Function call
        lambda m: translateFunction(
            m.group(1)) + "(" + parse(m.group(2)) + ")"),

        (r"\((.+)\)\((.+)\)",  # Parenthesized implied multiplication
        lambda m: "(" + parse(m.group(1)) + ")*(" + parse(m.group(2)) + ")"),

        (r"\A\((.+)\)\Z",  # Parenthesized expression
        lambda m: "(" + parse(m.group(1)) + ")"),

        (r"\A(.*[\w\.])\((.+)\)\Z",  # Implied multiplication - a(b)
        lambda m: parse(m.group(1)) + "*(" + parse(m.group(2)) + ")"),

        (r"\A\((.+)\)([\w\.].*)\Z",  # Implied multiplication - (a)b
        lambda m: "(" + parse(m.group(1)) + ")*" + parse(m.group(2))),

        (r"\A(-? *[\d\.]+)([a-zA-Z].*)\Z",  # Implied multiplication - 2a
        lambda m: parse(m.group(1)) + "*" + parse(m.group(2))),

        (r"\A([^=]+)([\^\-\*/\+=]=?)(.+)\Z",  # Infix operator
        lambda m: parse(m.group(1)) + translateOperator(m.group(2)) + parse(m.group(3))))
    # End rules

    for rule, action in rules:
        m = match(rule, s)
        if m:
            return action(m)

    return s


def translateFunction(s):
    """
    Translate a string based on specific rules.
    
    This function translates a given string `s` according to the following rules:
    - If the string starts with "Arc", it replaces "Arc" with "a" and returns the result in lowercase.
    - Otherwise, it returns the string in lowercase.
    
    Parameters:
    s (str): The input string to be translated.
    
    Returns:
    str: The translated string.
    
    Examples:
    >>> translateFunction("ArcTan")
    'atan'
    >>> translateFunction("
    """

    if s.startswith("Arc"):
        return "a" + s[3:]
    return s.lower()


def translateOperator(s):
    dictionary = {'^': '**'}
    if s in dictionary:
        return dictionary[s]
    return s
