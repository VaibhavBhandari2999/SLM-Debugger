from __future__ import print_function, division

from re import match
from sympy import sympify


def mathematica(s):
    return sympify(parse(s))


def parse(s):
    """
    Parse a mathematical expression string into a simplified form.
    
    This function takes a string representing a mathematical expression and
    parses it according to a set of defined rules. The parsed expression is
    returned in a simplified form.
    
    Parameters:
    s (str): The input string representing a mathematical expression.
    
    Returns:
    str: The simplified and parsed mathematical expression.
    
    Rules:
    1. Arithmetic operation between a constant and a function.
    2. Arithmetic operation between two functions.
    3. Function call.
    4. Parenthesized
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
    
    Args:
    s (str): The input string to be translated.
    
    Returns:
    str: The translated string.
    
    Notes:
    - If the string starts with 'Arc', it is translated to 'a' followed by the substring starting from the 4th character.
    - Otherwise, the string is converted to lowercase.
    """

    if s.startswith("Arc"):
        return "a" + s[3:]
    return s.lower()


def translateOperator(s):
    """
    Translate a given operator string to its equivalent Python operator.
    
    Args:
    s (str): The operator string to be translated. Currently supports the caret '^' which is translated to '**'.
    
    Returns:
    str: The translated operator string.
    
    Examples:
    >>> translateOperator('^')
    '**'
    >>> translateOperator('+')
    '+'
    """

    dictionary = {'^': '**'}
    if s in dictionary:
        return dictionary[s]
    return s
