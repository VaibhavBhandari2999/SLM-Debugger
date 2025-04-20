from __future__ import print_function, division

from sympy.core import Basic


class CartanType_generator(Basic):
    """
    Constructor for actually creating things
    """
    def __call__(self, *args):
        """
        Constructs a Lie algebra of a specified type and rank.
        
        This function takes a string or a list as an argument to determine the type and rank of the Lie algebra. The string should be in the format 'LetterRank' (e.g., 'A3' for A(3)) or a list in the format ['Letter', Rank] (e.g., ['A', 3] for A(3)).
        
        Parameters:
        - c (str or list): The type and rank of the
        """

        c = args[0]
        if type(c) == list:
            letter, n = c[0], int(c[1])
        elif type(c) == str:
            letter, n = c[0], int(c[1:])
        else:
            raise TypeError("Argument must be a string (e.g. 'A3') or a list (e.g. ['A', 3])")

        if n < 0:
            raise ValueError("Lie algebra rank cannot be negative")
        if letter == "A":
            from . import type_a
            return type_a.TypeA(n)
        if letter == "B":
            from . import type_b
            return type_b.TypeB(n)

        if letter == "C":
            from . import type_c
            return type_c.TypeC(n)

        if letter == "D":
            from . import type_d
            return type_d.TypeD(n)

        if letter == "E":
            if n >= 6 and n <= 8:
                from . import type_e
                return type_e.TypeE(n)

        if letter == "F":
            if n == 4:
                from . import type_f
                return type_f.TypeF(n)

        if letter == "G":
            if n == 2:
                from . import type_g
                return type_g.TypeG(n)

CartanType = CartanType_generator()


class Standard_Cartan(Basic):
    """
    Concrete base class for Cartan types such as A4, etc
    """

    def __new__(cls, series, n):
        """
        Constructs a new instance of a class derived from Basic.
        
        This method is the special method that creates a new instance of the class. It takes a series and an integer n as input parameters. The series is a sequence of data points, and n is an integer used for some computation or analysis within the class.
        
        Parameters:
        cls (type): The class itself, used for inheritance.
        series (sequence): A sequence of data points.
        n (int): An integer used for some computation
        """

        obj = Basic.__new__(cls, series, n)
        obj.n = n
        obj.series = series
        return obj

    def rank(self):
        """
        Returns the rank of the Lie algebra
        """
        return self.n

    def series(self):
        """
        Returns the type of the Lie algebra
        """
        return self.series
