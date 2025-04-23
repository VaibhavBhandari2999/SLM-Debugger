# -*- coding: utf-8 -*-

from __future__ import print_function, division

import keyword as kw
import sympy
from .repr import ReprPrinter
from .str import StrPrinter

# A list of classes that should be printed using StrPrinter
STRPRINT = ("Add", "Infinity", "Integer", "Mul", "NegativeInfinity",
            "Pow", "Zero")


class PythonPrinter(ReprPrinter, StrPrinter):
    """A printer which converts an expression into its Python interpretation."""

    def __init__(self, settings=None):
        """
        Initialize the PythonPrinter with optional settings.
        
        This method initializes the PythonPrinter object, setting up the necessary
        print methods and configurations. It uses the ReprPrinter and StrPrinter
        classes to handle different printing behaviors. The PythonPrinter is
        configured to use StrPrinter for specific classes that require different
        output formatting.
        
        Parameters:
        settings (dict, optional): A dictionary containing settings for the printer.
        If not provided, default settings will be used.
        
        Attributes Set:
        - symbols: A list to store
        """

        ReprPrinter.__init__(self)
        StrPrinter.__init__(self, settings)
        self.symbols = []
        self.functions = []

        # Create print methods for classes that should use StrPrinter instead
        # of ReprPrinter.
        for name in STRPRINT:
            f_name = "_print_%s" % name
            f = getattr(StrPrinter, f_name)
            setattr(PythonPrinter, f_name, f)

    def _print_Function(self, expr):
        """
        Prints a function from the given expression.
        
        This method is used to print a function from the provided expression. If the function is not recognized by SymPy and is not already in the list of custom functions, it is added to the list. The function then calls the superclass method to print the function.
        
        Parameters:
        expr (sympy.Expr): The SymPy expression from which to print the function.
        
        Returns:
        str: The string representation of the function in the expression.
        """

        func = expr.func.__name__
        if not hasattr(sympy, func) and not func in self.functions:
            self.functions.append(func)
        return StrPrinter._print_Function(self, expr)

    # procedure (!) for defining symbols which have be defined in print_python()
    def _print_Symbol(self, expr):
        symbol = self._str(expr)
        if symbol not in self.symbols:
            self.symbols.append(symbol)
        return StrPrinter._print_Symbol(self, expr)

    def _print_module(self, expr):
        raise ValueError('Modules in the expression are unacceptable')


def python(expr, **settings):
    """Return Python interpretation of passed expression
    (can be passed to the exec() function without any modifications)"""

    printer = PythonPrinter(settings)
    exprp = printer.doprint(expr)

    result = ''
    # Returning found symbols and functions
    renamings = {}
    for symbolname in printer.symbols:
        newsymbolname = symbolname
        # Escape symbol names that are reserved python keywords
        if kw.iskeyword(newsymbolname):
            while True:
                newsymbolname += "_"
                if (newsymbolname not in printer.symbols and
                        newsymbolname not in printer.functions):
                    renamings[sympy.Symbol(
                        symbolname)] = sympy.Symbol(newsymbolname)
                    break
        result += newsymbolname + ' = Symbol(\'' + symbolname + '\')\n'

    for functionname in printer.functions:
        newfunctionname = functionname
        # Escape function names that are reserved python keywords
        if kw.iskeyword(newfunctionname):
            while True:
                newfunctionname += "_"
                if (newfunctionname not in printer.symbols and
                        newfunctionname not in printer.functions):
                    renamings[sympy.Function(
                        functionname)] = sympy.Function(newfunctionname)
                    break
        result += newfunctionname + ' = Function(\'' + functionname + '\')\n'

    if not len(renamings) == 0:
        exprp = expr.subs(renamings)
    result += 'e = ' + printer._str(exprp)
    return result


def print_python(expr, **settings):
    """Print output of python() function"""
    print(python(expr, **settings))
