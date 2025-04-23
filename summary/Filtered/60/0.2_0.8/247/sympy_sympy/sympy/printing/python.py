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
        Initialize the PythonPrinter.
        
        This method initializes the PythonPrinter by calling the constructors of ReprPrinter and StrPrinter with the provided settings. It also sets up the symbols and functions lists. Additionally, it dynamically generates print methods for classes specified in the STRPRINT list, using the print methods from the StrPrinter class.
        
        Parameters:
        settings (dict, optional): A dictionary containing settings for the printer.
        
        Returns:
        None
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
        Prints a function in a specified format.
        
        This method is used to print a given SymPy expression's function in a specific manner. It checks if the function name is not in the SymPy module or the list of custom functions, and if not, it adds the function name to the list of custom functions. Then, it calls the superclass method to print the function.
        
        Parameters:
        expr (sympy.Expr): The SymPy expression whose function needs to be printed.
        
        Returns:
        str: The
        """

        func = expr.func.__name__
        if not hasattr(sympy, func) and not func in self.functions:
            self.functions.append(func)
        return StrPrinter._print_Function(self, expr)

    # procedure (!) for defining symbols which have be defined in print_python()
    def _print_Symbol(self, expr):
        """
        Prints a symbolic expression as a string and registers the symbol if it is not already registered.
        
        This method takes a symbolic expression and converts it to a string representation. If the string representation of the symbol is not already in the `symbols` list, it appends it. The method then returns the string representation of the expression.
        
        Parameters:
        expr (Symbol): The symbolic expression to be printed.
        
        Returns:
        str: The string representation of the symbolic expression.
        
        Attributes:
        symbols (list): A list of
        """

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
