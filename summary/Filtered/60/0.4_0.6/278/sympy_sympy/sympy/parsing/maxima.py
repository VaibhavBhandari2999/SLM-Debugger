from __future__ import print_function, division

import re
from sympy import sympify, Sum, product, sin, cos


class MaximaHelpers:
    def maxima_expand(expr):
        return expr.expand()

    def maxima_float(expr):
        return expr.evalf()

    def maxima_trigexpand(expr):
        return expr.expand(trig=True)

    def maxima_sum(a1, a2, a3, a4):
        return Sum(a1, (a2, a3, a4)).doit()

    def maxima_product(a1, a2, a3, a4):
        return product(a1, (a2, a3, a4))

    def maxima_csc(expr):
        return 1/sin(expr)

    def maxima_sec(expr):
        return 1/cos(expr)

sub_dict = {
    'pi': re.compile(r'%pi'),
    'E': re.compile(r'%e'),
    'I': re.compile(r'%i'),
    '**': re.compile(r'\^'),
    'oo': re.compile(r'\binf\b'),
    '-oo': re.compile(r'\bminf\b'),
    "'-'": re.compile(r'\bminus\b'),
    'maxima_expand': re.compile(r'\bexpand\b'),
    'maxima_float': re.compile(r'\bfloat\b'),
    'maxima_trigexpand': re.compile(r'\btrigexpand'),
    'maxima_sum': re.compile(r'\bsum\b'),
    'maxima_product': re.compile(r'\bproduct\b'),
    'cancel': re.compile(r'\bratsimp\b'),
    'maxima_csc': re.compile(r'\bcsc\b'),
    'maxima_sec': re.compile(r'\bsec\b')
}

var_name = re.compile(r'^\s*(\w+)\s*:')


def parse_maxima(str, globals=None, name_dict={}):
    """
    Parses a string as Maxima code and evaluates it.
    
    This function takes a string representing Maxima code and optionally a dictionary of global variables and a dictionary of name substitutions. It processes the string, performs the necessary substitutions, and evaluates the resulting expression using SymPy. If a variable name is found in the string, it assigns the evaluated result to that variable in the provided global dictionary.
    
    Parameters:
    str (str): The string containing Maxima code to be parsed and evaluated.
    globals
    """

    str = str.strip()
    str = str.rstrip('; ')

    for k, v in sub_dict.items():
        str = v.sub(k, str)

    assign_var = None
    var_match = var_name.search(str)
    if var_match:
        assign_var = var_match.group(1)
        str = str[var_match.end():].strip()

    dct = MaximaHelpers.__dict__.copy()
    dct.update(name_dict)
    obj = sympify(str, locals=dct)

    if assign_var and globals:
        globals[assign_var] = obj

    return obj
