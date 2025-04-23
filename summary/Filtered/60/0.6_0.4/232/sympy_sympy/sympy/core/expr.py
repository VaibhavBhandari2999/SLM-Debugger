from __future__ import print_function, division

from .sympify import sympify, _sympify, SympifyError
from .basic import Basic, Atom
from .singleton import S
from .evalf import EvalfMixin, pure_complex
from .decorators import _sympifyit, call_highest_priority
from .cache import cacheit
from .compatibility import reduce, as_int, default_sort_key, range
from mpmath.libmp import mpf_log, prec_to_dps

from collections import defaultdict

class Expr(Basic, EvalfMixin):
    """
    Base class for algebraic expressions.

    Everything that requires arithmetic operations to be defined
    should subclass this class, instead of Basic (which should be
    used only for argument storage and expression manipulation, i.e.
    pattern matching, substitutions, etc).

    See Also
    ========

    sympy.core.basic.Basic
    """

    __slots__ = []

    @property
    def _diff_wrt(self):
        """Is it allowed to take derivative wrt to this instance.

        This determines if it is allowed to take derivatives wrt this object.
        Subclasses such as Symbol, Function and Derivative should return True
        to enable derivatives wrt them. The implementation in Derivative
        separates the Symbol and non-Symbol _diff_wrt=True variables and
        temporarily converts the non-Symbol vars in Symbols when performing
        the differentiation.

        Note, see the docstring of Derivative for how this should work
        mathematically. In particular, note that expr.subs(yourclass, Symbol)
        should be well-defined on a structural level, or this will lead to
        inconsistent results.

        Examples
        ========

        >>> from sympy import Expr
        >>> e = Expr()
        >>> e._diff_wrt
        False
        >>> class MyClass(Expr):
        ...     _diff_wrt = True
        ...
        >>> (2*MyClass()).diff(MyClass())
        2
        """
        return False

    @cacheit
    def sort_key(self, order=None):

        coeff, expr = self.as_coeff_Mul()

        if expr.is_Pow:
            expr, exp = expr.args
        else:
            expr, exp = expr, S.One

        if expr.is_Dummy:
            args = (expr.sort_key(),)
        elif expr.is_Atom:
            args = (str(expr),)
        else:
            if expr.is_Add:
                args = expr.as_ordered_terms(order=order)
            elif expr.is_Mul:
                args = expr.as_ordered_factors(order=order)
            else:
                args = expr.args

            args = tuple(
                [ default_sort_key(arg, order=order) for arg in args ])

        args = (len(args), tuple(args))
        exp = exp.sort_key(order=order)

        return expr.class_key(), args, exp, coeff

    # ***************
    # * Arithmetics *
    # ***************
    # Expr and its sublcasses use _op_priority to determine which object
    # passed to a binary special method (__mul__, etc.) will handle the
    # operation. In general, the 'call_highest_priority' decorator will choose
    # the object with the highest _op_priority to handle the call.
    # Custom subclasses that want to define their own binary special methods
    # should set an _op_priority value that is higher than the default.
    #
    # **NOTE**:
    # This is a temporary fix, and will eventually be replaced with
    # something better and more powerful.  See issue 5510.
    _op_priority = 10.0

    def __pos__(self):
        return self

    def __neg__(self):
        return Mul(S.NegativeOne, self)

    def __abs__(self):
        from sympy import Abs
        return Abs(self)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__radd__')
    def __add__(self, other):
        return Add(self, other)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__add__')
    def __radd__(self, other):
        return Add(other, self)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__rsub__')
    def __sub__(self, other):
        return Add(self, -other)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__sub__')
    def __rsub__(self, other):
        return Add(other, -self)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__rmul__')
    def __mul__(self, other):
        return Mul(self, other)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__mul__')
    def __rmul__(self, other):
        return Mul(other, self)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__rpow__')
    def __pow__(self, other):
        return Pow(self, other)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__pow__')
    def __rpow__(self, other):
        return Pow(other, self)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__rdiv__')
    def __div__(self, other):
        return Mul(self, Pow(other, S.NegativeOne))

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__div__')
    def __rdiv__(self, other):
        return Mul(other, Pow(self, S.NegativeOne))

    __truediv__ = __div__
    __rtruediv__ = __rdiv__

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__rmod__')
    def __mod__(self, other):
        return Mod(self, other)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__mod__')
    def __rmod__(self, other):
        return Mod(other, self)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__rfloordiv__')
    def __floordiv__(self, other):
        from sympy.functions.elementary.integers import floor
        return floor(self / other)

    @_sympifyit('other', NotImplemented)
    @call_highest_priority('__floordiv__')
    def __rfloordiv__(self, other):
        from sympy.functions.elementary.integers import floor
        return floor(self / other)

    def __int__(self):
        # Although we only need to round to the units position, we'll
        # get one more digit so the extra testing below can be avoided
        # unless the rounded value rounded to an integer, e.g. if an
        # expression were equal to 1.9 and we rounded to the unit position
        # we would get a 2 and would not know if this rounded up or not
        # without doing a test (as done below). But if we keep an extra
        # digit we know that 1.9 is not the same as 1 and there is no
        # need for further testing: our int value is correct. If the value
        # were 1.99, however, this would round to 2.0 and our int value is
        # off by one. So...if our round value is the same as the int value
        # (regardless of how much extra work we do to calculate extra decimal
        # places) we need to test whether we are off by one.
        from sympy import Dummy
        if not self.is_number:
            raise TypeError("can't convert symbols to int")
        r = self.round(2)
        if not r.is_Number:
            raise TypeError("can't convert complex to int")
        if r in (S.NaN, S.Infinity, S.NegativeInfinity):
            raise TypeError("can't convert %s to int" % r)
        i = int(r)
        if not i:
            return 0
        # off-by-one check
        if i == r and not (self - i).equals(0):
            isign = 1 if i > 0 else -1
            x = Dummy()
            # in the following (self - i).evalf(2) will not always work while
            # (self - r).evalf(2) and the use of subs does; if the test that
            # was added when this comment was added passes, it might be safe
            # to simply use sign to compute this rather than doing this by hand:
            diff_sign = 1 if (self - x).evalf(2, subs={x: i}) > 0 else -1
            if diff_sign != isign:
                i -= isign
        return i
    __long__ = __int__

    def __float__(self):
        # Don't bother testing if it's a number; if it's not this is going
        # to fail, and if it is we still need to check that it evalf'ed to
        # a number.
        result = self.evalf()
        if result.is_Number:
            return float(result)
        if result.is_number and result.as_real_imag()[1]:
            raise TypeError("can't convert complex to float")
        raise TypeError("can't convert expression to float")

    def __complex__(self):
        """
        Generate a complex number from the evaluated result of the current object.
        
        This method returns the complex number representation of the evaluated result of the object. The evaluation is performed using the `evalf` method, which computes the numerical value of the object. The real and imaginary parts of the result are extracted using the `as_real_imag` method and converted to floating-point numbers using the `float` function. The method returns a Python `complex` object.
        
        Parameters:
        None
        
        Returns:
        complex:
        """

        result = self.evalf()
        re, im = result.as_real_imag()
        return complex(float(re), float(im))

    def __ge__(self, other):
        from sympy import GreaterThan
        try:
            other = _sympify(other)
        except SympifyError:
            raise TypeError("Invalid comparison %s >= %s" % (self, other))
        for me in (self, other):
            if (me.is_complex and me.is_real is False) or \
                    me.has(S.ComplexInfinity):
                raise TypeError("Invalid comparison of complex %s" % me)
            if me is S.NaN:
                raise TypeError("Invalid NaN comparison")
        n2 = _n2(self, other)
        if n2 is not None:
            return _sympify(n2 >= 0)
        if self.is_real or other.is_real:
            dif = self - other
            if dif.is_nonnegative is not None and \
                    dif.is_nonnegative is not dif.is_negative:
                return sympify(dif.is_nonnegative)
        return GreaterThan(self, other, evaluate=False)

    def __le__(self, other):
        from sympy import LessThan
        try:
            other = _sympify(other)
        except SympifyError:
            raise TypeError("Invalid comparison %s <= %s" % (self, other))
        for me in (self, other):
            if (me.is_complex and me.is_real is False) or \
                    me.has(S.ComplexInfinity):
                raise TypeError("Invalid comparison of complex %s" % me)
            if me is S.NaN:
                raise TypeError("Invalid NaN comparison")
        n2 = _n2(self, other)
        if n2 is not None:
            return _sympify(n2 <= 0)
        if self.is_real or other.is_real:
            dif = self - other
            if dif.is_nonpositive is not None and \
                    dif.is_nonpositive is not dif.is_positive:
                return sympify(dif.is_nonpositive)
        return LessThan(self, other, evaluate=False)

    def __gt__(self, other):
        """
        Compares two expressions to determine if the first is greater than the second.
        
        This method is used to compare two SymPy expressions and returns a Boolean result indicating whether the first expression is strictly greater than the second. It handles various types of expressions, including complex numbers and NaN values, and raises appropriate exceptions for invalid comparisons.
        
        Parameters:
        self (Expr): The first SymPy expression to compare.
        other (Expr): The second SymPy expression to compare.
        
        Returns:
        bool: True if the
        """

        from sympy import StrictGreaterThan
        try:
            other = _sympify(other)
        except SympifyError:
            raise TypeError("Invalid comparison %s > %s" % (self, other))
        for me in (self, other):
            if (me.is_complex and me.is_real is False) or \
                    me.has(S.ComplexInfinity):
                raise TypeError("Invalid comparison of complex %s" % me)
            if me is S.NaN:
                raise TypeError("Invalid NaN comparison")
        n2 = _n2(self, other)
        if n2 is not None:
            return _sympify(n2 > 0)
        if self.is_real or other.is_real:
            dif = self - other
            if dif.is_positive is not None and \
                    dif.is_positive is not dif.is_nonpositive:
                return sympify(dif.is_positive)
        return StrictGreaterThan(self, other, evaluate=False)

    def __lt__(self, other):
        from sympy import StrictLessThan
        try:
            other = _sympify(other)
        except SympifyError:
            raise TypeError("Invalid comparison %s < %s" % (self, other))
        for me in (self, other):
            if (me.is_complex and me.is_real is False) or \
                    me.has(S.ComplexInfinity):
                raise TypeError("Invalid comparison of complex %s" % me)
            if me is S.NaN:
                raise TypeError("Invalid NaN comparison")
        n2 = _n2(self, other)
        if n2 is not None:
            return _sympify(n2 < 0)
        if self.is_real or other.is_real:
            dif = self - other
            if dif.is_negative is not None and \
                    dif.is_negative is not dif.is_nonnegative:
                return sympify(dif.is_negative)
        return StrictLessThan(self, other, evaluate=False)

    @staticmethod
    def _from_mpmath(x, prec):
        from sympy import Float
        if hasattr(x, "_mpf_"):
            return Float._new(x._mpf_, prec)
        elif hasattr(x, "_mpc_"):
            re, im = x._mpc_
            re = Float._new(re, prec)
            im = Float._new(im, prec)*S.ImaginaryUnit
            return re + im
        else:
            raise TypeError("expected mpmath number (mpf or mpc)")

    @property
    def is_number(self):
        """Returns True if ``self`` has no free symbols.
        It will be faster than ``if not self.free_symbols``, however, since
        ``is_number`` will fail as soon as it hits a free symbol.

        Examples
        ========

        >>> from sympy import log, Integral
        >>> from sympy.abc import x

        >>> x.is_number
        False
        >>> (2*x).is_number
        False
        >>> (2 + log(2)).is_number
        True
        >>> (2 + Integral(2, x)).is_number
        False
        >>> (2 + Integral(2, (x, 1, 2))).is_number
        True

        """
        return all(obj.is_number for obj in self.args)

    def _random(self, n=None, re_min=-1, im_min=-1, re_max=1, im_max=1):
        """Return self evaluated, if possible, replacing free symbols with
        random complex values, if necessary.

        The random complex value for each free symbol is generated
        by the random_complex_number routine giving real and imaginary
        parts in the range given by the re_min, re_max, im_min, and im_max
        values. The returned value is evaluated to a precision of n
        (if given) else the maximum of 15 and the precision needed
        to get more than 1 digit of precision. If the expression
        could not be evaluated to a number, or could not be evaluated
        to more than 1 digit of precision, then None is returned.

        Examples
        ========

        >>> from sympy import sqrt
        >>> from sympy.abc import x, y
        >>> x._random()                         # doctest: +SKIP
        0.0392918155679172 + 0.916050214307199*I
        >>> x._random(2)                        # doctest: +SKIP
        -0.77 - 0.87*I
        >>> (x + y/2)._random(2)                # doctest: +SKIP
        -0.57 + 0.16*I
        >>> sqrt(2)._random(2)
        1.4

        See Also
        ========

        sympy.utilities.randtest.random_complex_number
        """

        free = self.free_symbols
        prec = 1
        if free:
            from sympy.utilities.randtest import random_complex_number
            a, c, b, d = re_min, re_max, im_min, im_max
            reps = dict(list(zip(free, [random_complex_number(a, b, c, d, rational=True)
                           for zi in free])))
            try:
                nmag = abs(self.evalf(2, subs=reps))
            except (ValueError, TypeError):
                # if an out of range value resulted in evalf problems
                # then return None -- XXX is there a way to know how to
                # select a good random number for a given expression?
                # e.g. when calculating n! negative values for n should not
                # be used
                return None
        else:
            reps = {}
            nmag = abs(self.evalf(2))

        if not hasattr(nmag, '_prec'):
            # e.g. exp_polar(2*I*pi) doesn't evaluate but is_number is True
            return None

        if nmag._prec == 1:
            # increase the precision up to the default maximum
            # precision to see if we can get any significance

            from mpmath.libmp.libintmath import giant_steps
            from sympy.core.evalf import DEFAULT_MAXPREC as target

            # evaluate
            for prec in giant_steps(2, target):
                nmag = abs(self.evalf(prec, subs=reps))
                if nmag._prec != 1:
                    break

        if nmag._prec != 1:
            if n is None:
                n = max(prec, 15)
            return self.evalf(n, subs=reps)

        # never got any significance
        return None

    def is_constant(self, *wrt, **flags):
        """Return True if self is constant, False if not, or None if
        the constancy could not be determined conclusively.

        If an expression has no free symbols then it is a constant. If
        there are free symbols it is possible that the expression is a
        constant, perhaps (but not necessarily) zero. To test such
        expressions, two strategies are tried:

        1) numerical evaluation at two random points. If two such evaluations
        give two different values and the values have a precision greater than
        1 then self is not constant. If the evaluations agree or could not be
        obtained with any precision, no decision is made. The numerical testing
        is done only if ``wrt`` is different than the free symbols.

        2) differentiation with respect to variables in 'wrt' (or all free
        symbols if omitted) to see if the expression is constant or not. This
        will not always lead to an expression that is zero even though an
        expression is constant (see added test in test_expr.py). If
        all derivatives are zero then self is constant with respect to the
        given symbols.

        If neither evaluation nor differentiation can prove the expression is
        constant, None is returned unless two numerical values happened to be
        the same and the flag ``failing_number`` is True -- in that case the
        numerical value will be returned.

        If flag simplify=False is passed, self will not be simplified;
        the default is True since self should be simplified before testing.

        Examples
        ========

        >>> from sympy import cos, sin, Sum, S, pi
        >>> from sympy.abc import a, n, x, y
        >>> x.is_constant()
        False
        >>> S(2).is_constant()
        True
        >>> Sum(x, (x, 1, 10)).is_constant()
        True
        >>> Sum(x, (x, 1, n)).is_constant()
        False
        >>> Sum(x, (x, 1, n)).is_constant(y)
        True
        >>> Sum(x, (x, 1, n)).is_constant(n)
        False
        >>> Sum(x, (x, 1, n)).is_constant(x)
        True
        >>> eq = a*cos(x)**2 + a*sin(x)**2 - a
        >>> eq.is_constant()
        True
        >>> eq.subs({x: pi, a: 2}) == eq.subs({x: pi, a: 3}) == 0
        True

        >>> (0**x).is_constant()
        False
        >>> x.is_constant()
        False
        >>> (x**x).is_constant()
        False
        >>> one = cos(x)**2 + sin(x)**2
        >>> one.is_constant()
        True
        >>> ((one - 1)**(x + 1)).is_constant() in (True, False) # could be 0 or 1
        True
        """

        simplify = flags.get('simplify', True)

        # Except for expressions that contain units, only one of these should
        # be necessary since if something is
        # known to be a number it should also know that there are no
        # free symbols. But is_number quits as soon as it hits a non-number
        # whereas free_symbols goes until all free symbols have been collected,
        # thus is_number should be faster. But a double check on free symbols
        # is made just in case there is a discrepancy between the two.
        free = self.free_symbols
        if self.is_number or not free:
            # if the following assertion fails then that object's free_symbols
            # method needs attention: if an expression is a number it cannot
            # have free symbols
            assert not free
            return True

        # if we are only interested in some symbols and they are not in the
        # free symbols then this expression is constant wrt those symbols
        wrt = set(wrt)
        if wrt and not wrt & free:
            return True
        wrt = wrt or free

        # simplify unless this has already been done
        expr = self
        if simplify:
            expr = expr.simplify()

        # is_zero should be a quick assumptions check; it can be wrong for
        # numbers (see test_is_not_constant test), giving False when it
        # shouldn't, but hopefully it will never give True unless it is sure.
        if expr.is_zero:
            return True

        # try numerical evaluation to see if we get two different values
        failing_number = None
        if wrt == free:
            # try 0 (for a) and 1 (for b)
            try:
                a = expr.subs(list(zip(free, [0]*len(free))),
                    simultaneous=True)
                if a is S.NaN:
                    # evaluation may succeed when substitution fails
                    a = expr._random(None, 0, 0, 0, 0)
            except ZeroDivisionError:
                a = None
            if a is not None and a is not S.NaN:
                try:
                    b = expr.subs(list(zip(free, [1]*len(free))),
                        simultaneous=True)
                    if b is S.NaN:
                        # evaluation may succeed when substitution fails
                        b = expr._random(None, 1, 0, 1, 0)
                except ZeroDivisionError:
                    b = None
                if b is not None and b is not S.NaN and b.equals(a) is False:
                    return False
                # try random real
                b = expr._random(None, -1, 0, 1, 0)
                if b is not None and b is not S.NaN and b.equals(a) is False:
                    return False
                # try random complex
                b = expr._random()
                if b is not None and b is not S.NaN:
                    if b.equals(a) is False:
                        return False
                    failing_number = a if a.is_number else b

        # now we will test each wrt symbol (or all free symbols) to see if the
        # expression depends on them or not using differentiation. This is
        # not sufficient for all expressions, however, so we don't return
        # False if we get a derivative other than 0 with free symbols.
        for w in wrt:
            deriv = expr.diff(w)
            if simplify:
                deriv = deriv.simplify()
            if deriv != 0:
                if not (pure_complex(deriv, or_real=True)):
                    if flags.get('failing_number', False):
                        return failing_number
                    elif deriv.free_symbols:
                        # dead line provided _random returns None in such cases
                        return None
                return False
        return True

    def equals(self, other, failing_expression=False):
        """Return True if self == other, False if it doesn't, or None. If
        failing_expression is True then the expression which did not simplify
        to a 0 will be returned instead of None.

        If ``self`` is a Number (or complex number) that is not zero, then
        the result is False.

        If ``self`` is a number and has not evaluated to zero, evalf will be
        used to test whether the expression evaluates to zero. If it does so
        and the result has significance (i.e. the precision is either -1, for
        a Rational result, or is greater than 1) then the evalf value will be
        used to return True or False.

        """
        from sympy.simplify.simplify import nsimplify, simplify
        from sympy.solvers.solveset import solveset
        from sympy.polys.polyerrors import NotAlgebraic
        from sympy.polys.numberfields import minimal_polynomial

        other = sympify(other)
        if self == other:
            return True

        # they aren't the same so see if we can make the difference 0;
        # don't worry about doing simplification steps one at a time
        # because if the expression ever goes to 0 then the subsequent
        # simplification steps that are done will be very fast.
        diff = factor_terms(simplify(self - other), radical=True)

        if not diff:
            return True

        if not diff.has(Add, Mod):
            # if there is no expanding to be done after simplifying
            # then this can't be a zero
            return False

        constant = diff.is_constant(simplify=False, failing_number=True)

        if constant is False:
            return False

        if constant is None and (diff.free_symbols or not diff.is_number):
            # e.g. unless the right simplification is done, a symbolic
            # zero is possible (see expression of issue 6829: without
            # simplification constant will be None).
            return

        if constant is True:
            ndiff = diff._random()
            if ndiff:
                return False

        # sometimes we can use a simplified result to give a clue as to
        # what the expression should be; if the expression is *not* zero
        # then we should have been able to compute that and so now
        # we can just consider the cases where the approximation appears
        # to be zero -- we try to prove it via minimal_polynomial.
        if diff.is_number:
            approx = diff.nsimplify()
            if not approx:
                # try to prove via self-consistency
                surds = [s for s in diff.atoms(Pow) if s.args[0].is_Integer]
                # it seems to work better to try big ones first
                surds.sort(key=lambda x: -x.args[0])
                for s in surds:
                    try:
                        # simplify is False here -- this expression has already
                        # been identified as being hard to identify as zero;
                        # we will handle the checking ourselves using nsimplify
                        # to see if we are in the right ballpark or not and if so
                        # *then* the simplification will be attempted.
                        if s.is_Symbol:
                            sol = list(solveset(diff, s))
                        else:
                            sol = [s]
                        if sol:
                            if s in sol:
                                return True
                            if s.is_real:
                                if any(nsimplify(si, [s]) == s and simplify(si) == s
                                        for si in sol):
                                    return True
                    except NotImplementedError:
                        pass

                # try to prove with minimal_polynomial but know when
                # *not* to use this or else it can take a long time. e.g. issue 8354
                if True:  # change True to condition that assures non-hang
                    try:
                        mp = minimal_polynomial(diff)
                        if mp.is_Symbol:
                            return True
                        return False
                    except (NotAlgebraic, NotImplementedError):
                        pass

        # diff has not simplified to zero; constant is either None, True
        # or the number with significance (prec != 1) that was randomly
        # calculated twice as the same value.
        if constant not in (True, None) and constant != 0:
            return False

        if failing_expression:
            return diff
        return None

    def _eval_is_positive(self):
        from sympy.polys.numberfields import minimal_polynomial
        from sympy.polys.polyerrors import NotAlgebraic
        if self.is_number:
            if self.is_real is False:
                return False
            try:
                # check to see that we can get a value
                n2 = self._eval_evalf(2)
                if n2 is None:
                    raise AttributeError
                if n2._prec == 1:  # no significance
                    raise AttributeError
                if n2 == S.NaN:
                    raise AttributeError
            except (AttributeError, ValueError):
                return None
            n, i = self.evalf(2).as_real_imag()
            if not i.is_Number or not n.is_Number:
                return False
            if n._prec != 1 and i._prec != 1:
                return bool(not i and n > 0)
            elif n._prec == 1 and (not i or i._prec == 1) and \
                    self.is_algebraic and not self.has(Function):
                try:
                    if minimal_polynomial(self).is_Symbol:
                        return False
                except (NotAlgebraic, NotImplementedError):
                    pass

    def _eval_is_negative(self):
        from sympy.polys.numberfields import minimal_polynomial
        from sympy.polys.polyerrors import NotAlgebraic
        if self.is_number:
            if self.is_real is False:
                return False
            try:
                # check to see that we can get a value
                n2 = self._eval_evalf(2)
                if n2 is None:
                    raise AttributeError
                if n2._prec == 1:  # no significance
                    raise AttributeError
                if n2 == S.NaN:
                    raise AttributeError
            except (AttributeError, ValueError):
                return None
            n, i = self.evalf(2).as_real_imag()
            if not i.is_Number or not n.is_Number:
                return False
            if n._prec != 1 and i._prec != 1:
                return bool(not i and n < 0)
            elif n._prec == 1 and (not i or i._prec == 1) and \
                    self.is_algebraic and not self.has(Function):
                try:
                    if minimal_polynomial(self).is_Symbol:
                        return False
                except (NotAlgebraic, NotImplementedError):
                    pass

    def _eval_interval(self, x, a, b):
        """
        Returns evaluation over an interval.  For most functions this is:

        self.subs(x, b) - self.subs(x, a),

        possibly using limit() if NaN is returned from subs.

        If b or a is None, it only evaluates -self.subs(x, a) or self.subs(b, x),
        respectively.

        """
        from sympy.series import limit, Limit
        from sympy.solvers.solveset import solveset
        from sympy.sets.sets import Interval

        if (a is None and b is None):
            raise ValueError('Both interval ends cannot be None.')

        if a == b:
            return 0

        if a is None:
            A = 0
        else:
            A = self.subs(x, a)
            if A.has(S.NaN, S.Infinity, S.NegativeInfinity, S.ComplexInfinity):
                if (a < b) != False:
                    A = limit(self, x, a,"+")
                else:
                    A = limit(self, x, a,"-")

                if A is S.NaN:
                    return A
                if isinstance(A, Limit):
                    raise NotImplementedError("Could not compute limit")

        if b is None:
            B = 0
        else:
            B = self.subs(x, b)
            if B.has(S.NaN, S.Infinity, S.NegativeInfinity, S.ComplexInfinity):
                if (a < b) != False:
                    B = limit(self, x, b,"-")
                else:
                    B = limit(self, x, b,"+")

                if isinstance(B, Limit):
                    raise NotImplementedError("Could not compute limit")

        if (a and b) is None:
            return B - A

        value = B - A

        if a.is_comparable and b.is_comparable:
            if a < b:
                domain = Interval(a, b)
            else:
                domain = Interval(b, a)
            singularities = list(solveset(self.cancel().as_numer_denom()[1], x, domain = domain))
            for s in singularities:
                if a < s < b:
                    value += -limit(self, x, s, "+") + limit(self, x, s, "-")
                elif b < s < a:
                    value += limit(self, x, s, "+") - limit(self, x, s, "-")

        return value

    def _eval_power(self, other):
        # subclass to compute self**other for cases when
        # other is not NaN, 0, or 1
        return None

    def _eval_conjugate(self):
        if self.is_real:
            return self
        elif self.is_imaginary:
            return -self

    def conjugate(self):
        from sympy.functions.elementary.complexes import conjugate as c
        return c(self)

    def _eval_transpose(self):
        from sympy.functions.elementary.complexes import conjugate
        if self.is_complex:
            return self
        elif self.is_hermitian:
            return conjugate(self)
        elif self.is_antihermitian:
            return -conjugate(self)

    def transpose(self):
        from sympy.functions.elementary.complexes import transpose
        return transpose(self)

    def _eval_adjoint(self):
        from sympy.functions.elementary.complexes import conjugate, transpose
        if self.is_hermitian:
            return self
        elif self.is_antihermitian:
            return -self
        obj = self._eval_conjugate()
        if obj is not None:
            return transpose(obj)
        obj = self._eval_transpose()
        if obj is not None:
            return conjugate(obj)

    def adjoint(self):
        from sympy.functions.elementary.complexes import adjoint
        return adjoint(self)

    @classmethod
    def _parse_order(cls, order):
        """Parse and configure the ordering of terms. """
        from sympy.polys.orderings import monomial_key

        try:
            reverse = order.startswith('rev-')
        except AttributeError:
            reverse = False
        else:
            if reverse:
                order = order[4:]

        monom_key = monomial_key(order)

        def neg(monom):
            result = []

            for m in monom:
                if isinstance(m, tuple):
                    result.append(neg(m))
                else:
                    result.append(-m)

            return tuple(result)

        def key(term):
            """
            Generate a key for sorting terms in a polynomial expression.
            
            This function is used to create a sorting key for polynomial terms. Each term is a tuple containing:
            - A coefficient tuple, which is a nested tuple of the form ((re, im), (re, im)), where re and im are real and imaginary parts, respectively.
            - A monomial, which is a tuple representing the variable part of the term.
            - A non-commutative part, which is a tuple of elements that are sorted
            """

            _, ((re, im), monom, ncpart) = term

            monom = neg(monom_key(monom))
            ncpart = tuple([e.sort_key(order=order) for e in ncpart])
            coeff = ((bool(im), im), (re, im))

            return monom, ncpart, coeff

        return key, reverse

    def as_ordered_factors(self, order=None):
        """Return list of ordered factors (if Mul) else [self]."""
        return [self]

    def as_ordered_terms(self, order=None, data=False):
        """
        Transform an expression to an ordered list of terms.

        Examples
        ========

        >>> from sympy import sin, cos
        >>> from sympy.abc import x

        >>> (sin(x)**2*cos(x) + sin(x)**2 + 1).as_ordered_terms()
        [sin(x)**2*cos(x), sin(x)**2, 1]

        """
        key, reverse = self._parse_order(order)
        terms, gens = self.as_terms()

        if not any(term.is_Order for term, _ in terms):
            ordered = sorted(terms, key=key, reverse=reverse)
        else:
            _terms, _order = [], []

            for term, repr in terms:
                if not term.is_Order:
                    _terms.append((term, repr))
                else:
                    _order.append((term, repr))

            ordered = sorted(_terms, key=key, reverse=True) \
                + sorted(_order, key=key, reverse=True)

        if data:
            return ordered, gens
        else:
            return [term for term, _ in ordered]

    def as_terms(self):
        """Transform an expression to a list of terms. """
        from .add import Add
        from .mul import Mul
        from .exprtools import decompose_power

        gens, terms = set([]), []

        for term in Add.make_args(self):
            coeff, _term = term.as_coeff_Mul()

            coeff = complex(coeff)
            cpart, ncpart = {}, []

            if _term is not S.One:
                for factor in Mul.make_args(_term):
                    if factor.is_number:
                        try:
                            coeff *= complex(factor)
                        except TypeError:
                            pass
                        else:
                            continue

                    if factor.is_commutative:
                        base, exp = decompose_power(factor)

                        cpart[base] = exp
                        gens.add(base)
                    else:
                        ncpart.append(factor)

            coeff = coeff.real, coeff.imag
            ncpart = tuple(ncpart)

            terms.append((term, (coeff, cpart, ncpart)))

        gens = sorted(gens, key=default_sort_key)

        k, indices = len(gens), {}

        for i, g in enumerate(gens):
            indices[g] = i

        result = []

        for term, (coeff, cpart, ncpart) in terms:
            monom = [0]*k

            for base, exp in cpart.items():
                monom[indices[base]] = exp

            result.append((term, (coeff, tuple(monom), ncpart)))

        return result, gens

    def removeO(self):
        """Removes the additive O(..) symbol if there is one"""
        return self

    def getO(self):
        """Returns the additive O(..) symbol if there is one, else None."""
        return None

    def getn(self):
        """
        Returns the order of the expression.

        The order is determined either from the O(...) term. If there
        is no O(...) term, it returns None.

        Examples
        ========

        >>> from sympy import O
        >>> from sympy.abc import x
        >>> (1 + x + O(x**2)).getn()
        2
        >>> (1 + x).getn()

        """
        from sympy import Dummy, Symbol
        o = self.getO()
        if o is None:
            return None
        elif o.is_Order:
            o = o.expr
            if o is S.One:
                return S.Zero
            if o.is_Symbol:
                return S.One
            if o.is_Pow:
                return o.args[1]
            if o.is_Mul:  # x**n*log(x)**n or x**n/log(x)**n
                for oi in o.args:
                    if oi.is_Symbol:
                        return S.One
                    if oi.is_Pow:
                        syms = oi.atoms(Symbol)
                        if len(syms) == 1:
                            x = syms.pop()
                            oi = oi.subs(x, Dummy('x', positive=True))
                            if oi.base.is_Symbol and oi.exp.is_Rational:
                                return abs(oi.exp)

        raise NotImplementedError('not sure of order of %s' % o)

    def count_ops(self, visual=None):
        """wrapper for count_ops that returns the operation count."""
        from .function import count_ops
        return count_ops(self, visual)

    def args_cnc(self, cset=False, warn=True, split_1=True):
        """Return [commutative factors, non-commutative factors] of self.

        self is treated as a Mul and the ordering of the factors is maintained.
        If ``cset`` is True the commutative factors will be returned in a set.
        If there were repeated factors (as may happen with an unevaluated Mul)
        then an error will be raised unless it is explicitly supressed by
        setting ``warn`` to False.

        Note: -1 is always separated from a Number unless split_1 is False.

        >>> from sympy import symbols, oo
        >>> A, B = symbols('A B', commutative=0)
        >>> x, y = symbols('x y')
        >>> (-2*x*y).args_cnc()
        [[-1, 2, x, y], []]
        >>> (-2.5*x).args_cnc()
        [[-1, 2.5, x], []]
        >>> (-2*x*A*B*y).args_cnc()
        [[-1, 2, x, y], [A, B]]
        >>> (-2*x*A*B*y).args_cnc(split_1=False)
        [[-2, x, y], [A, B]]
        >>> (-2*x*y).args_cnc(cset=True)
        [{-1, 2, x, y}, []]

        The arg is always treated as a Mul:

        >>> (-2 + x + A).args_cnc()
        [[], [x - 2 + A]]
        >>> (-oo).args_cnc() # -oo is a singleton
        [[-1, oo], []]
        """

        if self.is_Mul:
            args = list(self.args)
        else:
            args = [self]
        for i, mi in enumerate(args):
            if not mi.is_commutative:
                c = args[:i]
                nc = args[i:]
                break
        else:
            c = args
            nc = []

        if c and split_1 and (
            c[0].is_Number and
            c[0].is_negative and
                c[0] is not S.NegativeOne):
            c[:1] = [S.NegativeOne, -c[0]]

        if cset:
            clen = len(c)
            c = set(c)
            if clen and warn and len(c) != clen:
                raise ValueError('repeated commutative arguments: %s' %
                                 [ci for ci in c if list(self.args).count(ci) > 1])
        return [c, nc]

    def coeff(self, x, n=1, right=False):
        """
        Returns the coefficient from the term(s) containing ``x**n``. If ``n``
        is zero then all terms independent of ``x`` will be returned.

        When ``x`` is noncommutative, the coefficient to the left (default) or
        right of ``x`` can be returned. The keyword 'right' is ignored when
        ``x`` is commutative.

        See Also
        ========

        as_coefficient: separate the expression into a coefficient and factor
        as_coeff_Add: separate the additive constant from an expression
        as_coeff_Mul: separate the multiplicative constant from an expression
        as_independent: separate x-dependent terms/factors from others
        sympy.polys.polytools.coeff_monomial: efficiently find the single coefficient of a monomial in Poly
        sympy.polys.polytools.nth: like coeff_monomial but powers of monomial terms are used

        Examples
        ========

        >>> from sympy import symbols
        >>> from sympy.abc import x, y, z

        You can select terms that have an explicit negative in front of them:

        >>> (-x + 2*y).coeff(-1)
        x
        >>> (x - 2*y).coeff(-1)
        2*y

        You can select terms with no Rational coefficient:

        >>> (x + 2*y).coeff(1)
        x
        >>> (3 + 2*x + 4*x**2).coeff(1)
        0

        You can select terms independent of x by making n=0; in this case
        expr.as_independent(x)[0] is returned (and 0 will be returned instead
        of None):

        >>> (3 + 2*x + 4*x**2).coeff(x, 0)
        3
        >>> eq = ((x + 1)**3).expand() + 1
        >>> eq
        x**3 + 3*x**2 + 3*x + 2
        >>> [eq.coeff(x, i) for i in reversed(range(4))]
        [1, 3, 3, 2]
        >>> eq -= 2
        >>> [eq.coeff(x, i) for i in reversed(range(4))]
        [1, 3, 3, 0]

        You can select terms that have a numerical term in front of them:

        >>> (-x - 2*y).coeff(2)
        -y
        >>> from sympy import sqrt
        >>> (x + sqrt(2)*x).coeff(sqrt(2))
        x

        The matching is exact:

        >>> (3 + 2*x + 4*x**2).coeff(x)
        2
        >>> (3 + 2*x + 4*x**2).coeff(x**2)
        4
        >>> (3 + 2*x + 4*x**2).coeff(x**3)
        0
        >>> (z*(x + y)**2).coeff((x + y)**2)
        z
        >>> (z*(x + y)**2).coeff(x + y)
        0

        In addition, no factoring is done, so 1 + z*(1 + y) is not obtained
        from the following:

        >>> (x + z*(x + x*y)).coeff(x)
        1

        If such factoring is desired, factor_terms can be used first:

        >>> from sympy import factor_terms
        >>> factor_terms(x + z*(x + x*y)).coeff(x)
        z*(y + 1) + 1

        >>> n, m, o = symbols('n m o', commutative=False)
        >>> n.coeff(n)
        1
        >>> (3*n).coeff(n)
        3
        >>> (n*m + m*n*m).coeff(n) # = (1 + m)*n*m
        1 + m
        >>> (n*m + m*n*m).coeff(n, right=True) # = (1 + m)*n*m
        m

        If there is more than one possible coefficient 0 is returned:

        >>> (n*m + m*n).coeff(n)
        0

        If there is only one possible coefficient, it is returned:

        >>> (n*m + x*m*n).coeff(m*n)
        x
        >>> (n*m + x*m*n).coeff(m*n, right=1)
        1

        """
        x = sympify(x)
        if not isinstance(x, Basic):
            return S.Zero

        n = as_int(n)

        if not x:
            return S.Zero

        if x == self:
            if n == 1:
                return S.One
            return S.Zero

        if x is S.One:
            co = [a for a in Add.make_args(self)
                  if a.as_coeff_Mul()[0] is S.One]
            if not co:
                return S.Zero
            return Add(*co)

        if n == 0:
            if x.is_Add and self.is_Add:
                c = self.coeff(x, right=right)
                if not c:
                    return S.Zero
                if not right:
                    return self - Add(*[a*x for a in Add.make_args(c)])
                return self - Add(*[x*a for a in Add.make_args(c)])
            return self.as_independent(x, as_Add=True)[0]

        # continue with the full method, looking for this power of x:
        x = x**n

        def incommon(l1, l2):
            if not l1 or not l2:
                return []
            n = min(len(l1), len(l2))
            for i in range(n):
                if l1[i] != l2[i]:
                    return l1[:i]
            return l1[:]

        def find(l, sub, first=True):
            """ Find where list sub appears in list l. When ``first`` is True
            the first occurance from the left is returned, else the last
            occurance is returned. Return None if sub is not in l.

            >> l = range(5)*2
            >> find(l, [2, 3])
            2
            >> find(l, [2, 3], first=0)
            7
            >> find(l, [2, 4])
            None

            """
            if not sub or not l or len(sub) > len(l):
                return None
            n = len(sub)
            if not first:
                l.reverse()
                sub.reverse()
            for i in range(0, len(l) - n + 1):
                if all(l[i + j] == sub[j] for j in range(n)):
                    break
            else:
                i = None
            if not first:
                l.reverse()
                sub.reverse()
            if i is not None and not first:
                i = len(l) - (i + n)
            return i

        co = []
        args = Add.make_args(self)
        self_c = self.is_commutative
        x_c = x.is_commutative
        if self_c and not x_c:
            return S.Zero

        if self_c:
            xargs = x.args_cnc(cset=True, warn=False)[0]
            for a in args:
                margs = a.args_cnc(cset=True, warn=False)[0]
                if len(xargs) > len(margs):
                    continue
                resid = margs.difference(xargs)
                if len(resid) + len(xargs) == len(margs):
                    co.append(Mul(*resid))
            if co == []:
                return S.Zero
            elif co:
                return Add(*co)
        elif x_c:
            xargs = x.args_cnc(cset=True, warn=False)[0]
            for a in args:
                margs, nc = a.args_cnc(cset=True)
                if len(xargs) > len(margs):
                    continue
                resid = margs.difference(xargs)
                if len(resid) + len(xargs) == len(margs):
                    co.append(Mul(*(list(resid) + nc)))
            if co == []:
                return S.Zero
            elif co:
                return Add(*co)
        else:  # both nc
            xargs, nx = x.args_cnc(cset=True)
            # find the parts that pass the commutative terms
            for a in args:
                margs, nc = a.args_cnc(cset=True)
                if len(xargs) > len(margs):
                    continue
                resid = margs.difference(xargs)
                if len(resid) + len(xargs) == len(margs):
                    co.append((resid, nc))
            # now check the non-comm parts
            if not co:
                return S.Zero
            if all(n == co[0][1] for r, n in co):
                ii = find(co[0][1], nx, right)
                if ii is not None:
                    if not right:
                        return Mul(Add(*[Mul(*r) for r, c in co]), Mul(*co[0][1][:ii]))
                    else:
                        return Mul(*co[0][1][ii + len(nx):])
            beg = reduce(incommon, (n[1] for n in co))
            if beg:
                ii = find(beg, nx, right)
                if ii is not None:
                    if not right:
                        gcdc = co[0][0]
                        for i in range(1, len(co)):
                            gcdc = gcdc.intersection(co[i][0])
                            if not gcdc:
                                break
                        return Mul(*(list(gcdc) + beg[:ii]))
                    else:
                        m = ii + len(nx)
                        return Add(*[Mul(*(list(r) + n[m:])) for r, n in co])
            end = list(reversed(
                reduce(incommon, (list(reversed(n[1])) for n in co))))
            if end:
                ii = find(end, nx, right)
                if ii is not None:
                    if not right:
                        return Add(*[Mul(*(list(r) + n[:-len(end) + ii])) for r, n in co])
                    else:
                        return Mul(*end[ii + len(nx):])
            # look for single match
            hit = None
            for i, (r, n) in enumerate(co):
                ii = find(n, nx, right)
                if ii is not None:
                    if not hit:
                        hit = ii, r, n
                    else:
                        break
            else:
                if hit:
                    ii, r, n = hit
                    if not right:
                        return Mul(*(list(r) + n[:ii]))
                    else:
                        return Mul(*n[ii + len(nx):])

            return S.Zero

    def as_expr(self, *gens):
        """
        Convert a polynomial to a SymPy expression.

        Examples
        ========

        >>> from sympy import sin
        >>> from sympy.abc import x, y

        >>> f = (x**2 + x*y).as_poly(x, y)
        >>> f.as_expr()
        x**2 + x*y

        >>> sin(x).as_expr()
        sin(x)

        """
        return self

    def as_coefficient(self, expr):
        """
        Extracts symbolic coefficient at the given expression. In
        other words, this functions separates 'self' into the product
        of 'expr' and 'expr'-free coefficient. If such separation
        is not possible it will return None.

        Examples
        ========

        >>> from sympy import E, pi, sin, I, Poly
        >>> from sympy.abc import x

        >>> E.as_coefficient(E)
        1
        >>> (2*E).as_coefficient(E)
        2
        >>> (2*sin(E)*E).as_coefficient(E)

        Two terms have E in them so a sum is returned. (If one were
        desiring the coefficient of the term exactly matching E then
        the constant from the returned expression could be selected.
        Or, for greater precision, a method of Poly can be used to
        indicate the desired term from which the coefficient is
        desired.)

        >>> (2*E + x*E).as_coefficient(E)
        x + 2
        >>> _.args[0]  # just want the exact match
        2
        >>> p = Poly(2*E + x*E); p
        Poly(x*E + 2*E, x, E, domain='ZZ')
        >>> p.coeff_monomial(E)
        2
        >>> p.nth(0, 1)
        2

        Since the following cannot be written as a product containing
        E as a factor, None is returned. (If the coefficient ``2*x`` is
        desired then the ``coeff`` method should be used.)

        >>> (2*E*x + x).as_coefficient(E)
        >>> (2*E*x + x).coeff(E)
        2*x

        >>> (E*(x + 1) + x).as_coefficient(E)

        >>> (2*pi*I).as_coefficient(pi*I)
        2
        >>> (2*I).as_coefficient(pi*I)

        See Also
        ========

        coeff: return sum of terms have a given factor
        as_coeff_Add: separate the additive constant from an expression
        as_coeff_Mul: separate the multiplicative constant from an expression
        as_independent: separate x-dependent terms/factors from others
        sympy.polys.polytools.coeff_monomial: efficiently find the single coefficient of a monomial in Poly
        sympy.polys.polytools.nth: like coeff_monomial but powers of monomial terms are used


        """

        r = self.extract_multiplicatively(expr)
        if r and not r.has(expr):
            return r

    def as_independent(self, *deps, **hint):
        """
        A mostly naive separation of a Mul or Add into arguments that are not
        are dependent on deps. To obtain as complete a separation of variables
        as possible, use a separation method first, e.g.:

        * separatevars() to change Mul, Add and Pow (including exp) into Mul
        * .expand(mul=True) to change Add or Mul into Add
        * .expand(log=True) to change log expr into an Add

        The only non-naive thing that is done here is to respect noncommutative
        ordering of variables and to always return (0, 0) for `self` of zero
        regardless of hints.

        For nonzero `self`, the returned tuple (i, d) has the
        following interpretation:

        * i will has no variable that appears in deps
        * d will be 1 or else have terms that contain variables that are in deps
        * if self is an Add then self = i + d
        * if self is a Mul then self = i*d
        * otherwise (self, S.One) or (S.One, self) is returned.

        To force the expression to be treated as an Add, use the hint as_Add=True

        Examples
        ========

        -- self is an Add

        >>> from sympy import sin, cos, exp
        >>> from sympy.abc import x, y, z

        >>> (x + x*y).as_independent(x)
        (0, x*y + x)
        >>> (x + x*y).as_independent(y)
        (x, x*y)
        >>> (2*x*sin(x) + y + x + z).as_independent(x)
        (y + z, 2*x*sin(x) + x)
        >>> (2*x*sin(x) + y + x + z).as_independent(x, y)
        (z, 2*x*sin(x) + x + y)

        -- self is a Mul

        >>> (x*sin(x)*cos(y)).as_independent(x)
        (cos(y), x*sin(x))

        non-commutative terms cannot always be separated out when self is a Mul

        >>> from sympy import symbols
        >>> n1, n2, n3 = symbols('n1 n2 n3', commutative=False)
        >>> (n1 + n1*n2).as_independent(n2)
        (n1, n1*n2)
        >>> (n2*n1 + n1*n2).as_independent(n2)
        (0, n1*n2 + n2*n1)
        >>> (n1*n2*n3).as_independent(n1)
        (1, n1*n2*n3)
        >>> (n1*n2*n3).as_independent(n2)
        (n1, n2*n3)
        >>> ((x-n1)*(x-y)).as_independent(x)
        (1, (x - y)*(x - n1))

        -- self is anything else:

        >>> (sin(x)).as_independent(x)
        (1, sin(x))
        >>> (sin(x)).as_independent(y)
        (sin(x), 1)
        >>> exp(x+y).as_independent(x)
        (1, exp(x + y))

        -- force self to be treated as an Add:

        >>> (3*x).as_independent(x, as_Add=True)
        (0, 3*x)

        -- force self to be treated as a Mul:

        >>> (3+x).as_independent(x, as_Add=False)
        (1, x + 3)
        >>> (-3+x).as_independent(x, as_Add=False)
        (1, x - 3)

        Note how the below differs from the above in making the
        constant on the dep term positive.

        >>> (y*(-3+x)).as_independent(x)
        (y, x - 3)

        -- use .as_independent() for true independence testing instead
           of .has(). The former considers only symbols in the free
           symbols while the latter considers all symbols

        >>> from sympy import Integral
        >>> I = Integral(x, (x, 1, 2))
        >>> I.has(x)
        True
        >>> x in I.free_symbols
        False
        >>> I.as_independent(x) == (I, 1)
        True
        >>> (I + x).as_independent(x) == (I, x)
        True

        Note: when trying to get independent terms, a separation method
        might need to be used first. In this case, it is important to keep
        track of what you send to this routine so you know how to interpret
        the returned values

        >>> from sympy import separatevars, log
        >>> separatevars(exp(x+y)).as_independent(x)
        (exp(y), exp(x))
        >>> (x + x*y).as_independent(y)
        (x, x*y)
        >>> separatevars(x + x*y).as_independent(y)
        (x, y + 1)
        >>> (x*(1 + y)).as_independent(y)
        (x, y + 1)
        >>> (x*(1 + y)).expand(mul=True).as_independent(y)
        (x, x*y)
        >>> a, b=symbols('a b', positive=True)
        >>> (log(a*b).expand(log=True)).as_independent(b)
        (log(a), log(b))

        See Also
        ========
        .separatevars(), .expand(log=True), Add.as_two_terms(),
        Mul.as_two_terms(), .as_coeff_add(), .as_coeff_mul()
        """
        from .symbol import Symbol
        from .add import _unevaluated_Add
        from .mul import _unevaluated_Mul
        from sympy.utilities.iterables import sift

        if self.is_zero:
            return S.Zero, S.Zero

        func = self.func
        if hint.get('as_Add', func is Add):
            want = Add
        else:
            want = Mul

        # sift out deps into symbolic and other and ignore
        # all symbols but those that are in the free symbols
        sym = set()
        other = []
        for d in deps:
            if isinstance(d, Symbol):  # Symbol.is_Symbol is True
                sym.add(d)
            else:
                other.append(d)

        def has(e):
            """return the standard has() if there are no literal symbols, else
            check to see that symbol-deps are in the free symbols."""
            has_other = e.has(*other)
            if not sym:
                return has_other
            return has_other or e.has(*(e.free_symbols & sym))

        if (want is not func or
                func is not Add and func is not Mul):
            if has(self):
                return (want.identity, self)
            else:
                return (self, want.identity)
        else:
            if func is Add:
                args = list(self.args)
            else:
                args, nc = self.args_cnc()

        d = sift(args, lambda x: has(x))
        depend = d[True]
        indep = d[False]
        if func is Add:  # all terms were treated as commutative
            return (Add(*indep), _unevaluated_Add(*depend))
        else:  # handle noncommutative by stopping at first dependent term
            for i, n in enumerate(nc):
                if has(n):
                    depend.extend(nc[i:])
                    break
                indep.append(n)
            return Mul(*indep), (
                Mul(*depend, evaluate=False) if nc else
                _unevaluated_Mul(*depend))

    def as_real_imag(self, deep=True, **hints):
        """Performs complex expansion on 'self' and returns a tuple
           containing collected both real and imaginary parts. This
           method can't be confused with re() and im() functions,
           which does not perform complex expansion at evaluation.

           However it is possible to expand both re() and im()
           functions and get exactly the same results as with
           a single call to this function.

           >>> from sympy import symbols, I

           >>> x, y = symbols('x,y', real=True)

           >>> (x + y*I).as_real_imag()
           (x, y)

           >>> from sympy.abc import z, w

           >>> (z + w*I).as_real_imag()
           (re(z) - im(w), re(w) + im(z))

        """
        from sympy import im, re
        if hints.get('ignore') == self:
            return None
        else:
            return (re(self), im(self))

    def as_powers_dict(self):
        """Return self as a dictionary of factors with each factor being
        treated as a power. The keys are the bases of the factors and the
        values, the corresponding exponents. The resulting dictionary should
        be used with caution if the expression is a Mul and contains non-
        commutative factors since the order that they appeared will be lost in
        the dictionary."""
        d = defaultdict(int)
        d.update(dict([self.as_base_exp()]))
        return d

    def as_coefficients_dict(self):
        """Return a dictionary mapping terms to their Rational coefficient.
        Since the dictionary is a defaultdict, inquiries about terms which
        were not present will return a coefficient of 0. If an expression is
        not an Add it is considered to have a single term.

        Examples
        ========

        >>> from sympy.abc import a, x
        >>> (3*x + a*x + 4).as_coefficients_dict()
        {1: 4, x: 3, a*x: 1}
        >>> _[a]
        0
        >>> (3*a*x).as_coefficients_dict()
        {a*x: 3}

        """
        c, m = self.as_coeff_Mul()
        if not c.is_Rational:
            c = S.One
            m = self
        d = defaultdict(int)
        d.update({m: c})
        return d

    def as_base_exp(self):
        # a -> b ** e
        return self, S.One

    def as_coeff_mul(self, *deps, **kwargs):
        """Return the tuple (c, args) where self is written as a Mul, ``m``.

        c should be a Rational multiplied by any factors of the Mul that are
        independent of deps.

        args should be a tuple of all other factors of m; args is empty
        if self is a Number or if self is independent of deps (when given).

        This should be used when you don't know if self is a Mul or not but
        you want to treat self as a Mul or if you want to process the
        individual arguments of the tail of self as a Mul.

        - if you know self is a Mul and want only the head, use self.args[0];
        - if you don't want to process the arguments of the tail but need the
          tail then use self.as_two_terms() which gives the head and tail;
        - if you want to split self into an independent and dependent parts
          use ``self.as_independent(*deps)``

        >>> from sympy import S
        >>> from sympy.abc import x, y
        >>> (S(3)).as_coeff_mul()
        (3, ())
        >>> (3*x*y).as_coeff_mul()
        (3, (x, y))
        >>> (3*x*y).as_coeff_mul(x)
        (3*y, (x,))
        >>> (3*y).as_coeff_mul(x)
        (3*y, ())
        """
        if deps:
            if not self.has(*deps):
                return self, tuple()
        return S.One, (self,)

    def as_coeff_add(self, *deps):
        """Return the tuple (c, args) where self is written as an Add, ``a``.

        c should be a Rational added to any terms of the Add that are
        independent of deps.

        args should be a tuple of all other terms of ``a``; args is empty
        if self is a Number or if self is independent of deps (when given).

        This should be used when you don't know if self is an Add or not but
        you want to treat self as an Add or if you want to process the
        individual arguments of the tail of self as an Add.

        - if you know self is an Add and want only the head, use self.args[0];
        - if you don't want to process the arguments of the tail but need the
          tail then use self.as_two_terms() which gives the head and tail.
        - if you want to split self into an independent and dependent parts
          use ``self.as_independent(*deps)``

        >>> from sympy import S
        >>> from sympy.abc import x, y
        >>> (S(3)).as_coeff_add()
        (3, ())
        >>> (3 + x).as_coeff_add()
        (3, (x,))
        >>> (3 + x + y).as_coeff_add(x)
        (y + 3, (x,))
        >>> (3 + y).as_coeff_add(x)
        (y + 3, ())

        """
        if deps:
            if not self.has(*deps):
                return self, tuple()
        return S.Zero, (self,)

    def primitive(self):
        """Return the positive Rational that can be extracted non-recursively
        from every term of self (i.e., self is treated like an Add). This is
        like the as_coeff_Mul() method but primitive always extracts a positive
        Rational (never a negative or a Float).

        Examples
        ========

        >>> from sympy.abc import x
        >>> (3*(x + 1)**2).primitive()
        (3, (x + 1)**2)
        >>> a = (6*x + 2); a.primitive()
        (2, 3*x + 1)
        >>> b = (x/2 + 3); b.primitive()
        (1/2, x + 6)
        >>> (a*b).primitive() == (1, a*b)
        True
        """
        if not self:
            return S.One, S.Zero
        c, r = self.as_coeff_Mul(rational=True)
        if c.is_negative:
            c, r = -c, -r
        return c, r

    def as_content_primitive(self, radical=False, clear=True):
        """This method should recursively remove a Rational from all arguments
        and return that (content) and the new self (primitive). The content
        should always be positive and ``Mul(*foo.as_content_primitive()) == foo``.
        The primitive need not be in canonical form and should try to preserve
        the underlying structure if possible (i.e. expand_mul should not be
        applied to self).

        Examples
        ========

        >>> from sympy import sqrt
        >>> from sympy.abc import x, y, z

        >>> eq = 2 + 2*x + 2*y*(3 + 3*y)

        The as_content_primitive function is recursive and retains structure:

        >>> eq.as_content_primitive()
        (2, x + 3*y*(y + 1) + 1)

        Integer powers will have Rationals extracted from the base:

        >>> ((2 + 6*x)**2).as_content_primitive()
        (4, (3*x + 1)**2)
        >>> ((2 + 6*x)**(2*y)).as_content_primitive()
        (1, (2*(3*x + 1))**(2*y))

        Terms may end up joining once their as_content_primitives are added:

        >>> ((5*(x*(1 + y)) + 2*x*(3 + 3*y))).as_content_primitive()
        (11, x*(y + 1))
        >>> ((3*(x*(1 + y)) + 2*x*(3 + 3*y))).as_content_primitive()
        (9, x*(y + 1))
        >>> ((3*(z*(1 + y)) + 2.0*x*(3 + 3*y))).as_content_primitive()
        (1, 6.0*x*(y + 1) + 3*z*(y + 1))
        >>> ((5*(x*(1 + y)) + 2*x*(3 + 3*y))**2).as_content_primitive()
        (121, x**2*(y + 1)**2)
        >>> ((5*(x*(1 + y)) + 2.0*x*(3 + 3*y))**2).as_content_primitive()
        (1, 121.0*x**2*(y + 1)**2)

        Radical content can also be factored out of the primitive:

        >>> (2*sqrt(2) + 4*sqrt(10)).as_content_primitive(radical=True)
        (2, sqrt(2)*(1 + 2*sqrt(5)))

        If clear=False (default is True) then content will not be removed
        from an Add if it can be distributed to leave one or more
        terms with integer coefficients.

        >>> (x/2 + y).as_content_primitive()
        (1/2, x + 2*y)
        >>> (x/2 + y).as_content_primitive(clear=False)
        (1, x/2 + y)
        """
        return S.One, self

    def as_numer_denom(self):
        """ expression -> a/b -> a, b

        This is just a stub that should be defined by
        an object's class methods to get anything else.

        See Also
        ========
        normal: return a/b instead of a, b
        """

        return self, S.One

    def normal(self):
        from .mul import _unevaluated_Mul
        n, d = self.as_numer_denom()
        if d is S.One:
            return n
        if d.is_Number:
            if d is S.One:
                return n
            else:
                return _unevaluated_Mul(n, 1/d)
        else:
            return n/d

    def extract_multiplicatively(self, c):
        """Return None if it's not possible to make self in the form
           c * something in a nice way, i.e. preserving the properties
           of arguments of self.

           >>> from sympy import symbols, Rational

           >>> x, y = symbols('x,y', real=True)

           >>> ((x*y)**3).extract_multiplicatively(x**2 * y)
           x*y**2

           >>> ((x*y)**3).extract_multiplicatively(x**4 * y)

           >>> (2*x).extract_multiplicatively(2)
           x

           >>> (2*x).extract_multiplicatively(3)

           >>> (Rational(1, 2)*x).extract_multiplicatively(3)
           x/6

        """
        from .function import _coeff_isneg

        c = sympify(c)
        if self is S.NaN:
            return None
        if c is S.One:
            return self
        elif c == self:
            return S.One

        if c.is_Add:
            cc, pc = c.primitive()
            if cc is not S.One:
                c = Mul(cc, pc, evaluate=False)

        if c.is_Mul:
            a, b = c.as_two_terms()
            x = self.extract_multiplicatively(a)
            if x is not None:
                return x.extract_multiplicatively(b)

        quotient = self / c
        if self.is_Number:
            if self is S.Infinity:
                if c.is_positive:
                    return S.Infinity
            elif self is S.NegativeInfinity:
                if c.is_negative:
                    return S.Infinity
                elif c.is_positive:
                    return S.NegativeInfinity
            elif self is S.ComplexInfinity:
                if not c.is_zero:
                    return S.ComplexInfinity
            elif self.is_Integer:
                if not quotient.is_Integer:
                    return None
                elif self.is_positive and quotient.is_negative:
                    return None
                else:
                    return quotient
            elif self.is_Rational:
                if not quotient.is_Rational:
                    return None
                elif self.is_positive and quotient.is_negative:
                    return None
                else:
                    return quotient
            elif self.is_Float:
                if not quotient.is_Float:
                    return None
                elif self.is_positive and quotient.is_negative:
                    return None
                else:
                    return quotient
        elif self.is_NumberSymbol or self.is_Symbol or self is S.ImaginaryUnit:
            if quotient.is_Mul and len(quotient.args) == 2:
                if quotient.args[0].is_Integer and quotient.args[0].is_positive and quotient.args[1] == self:
                    return quotient
            elif quotient.is_Integer and c.is_Number:
                return quotient
        elif self.is_Add:
            cs, ps = self.primitive()
            # assert cs >= 1
            if c.is_Number and c is not S.NegativeOne:
                # assert c != 1 (handled at top)
                if cs is not S.One:
                    if c.is_negative:
                        xc = -(cs.extract_multiplicatively(-c))
                    else:
                        xc = cs.extract_multiplicatively(c)
                    if xc is not None:
                        return xc*ps  # rely on 2-arg Mul to restore Add
                return  # |c| != 1 can only be extracted from cs
            if c == ps:
                return cs
            # check args of ps
            newargs = []
            for arg in ps.args:
                newarg = arg.extract_multiplicatively(c)
                if newarg is None:
                    return  # all or nothing
                newargs.append(newarg)
            # args should be in same order so use unevaluated return
            if cs is not S.One:
                return Add._from_args([cs*t for t in newargs])
            else:
                return Add._from_args(newargs)
        elif self.is_Mul:
            args = list(self.args)
            for i, arg in enumerate(args):
                newarg = arg.extract_multiplicatively(c)
                if newarg is not None:
                    args[i] = newarg
                    return Mul(*args)
        elif self.is_Pow:
            if c.is_Pow and c.base == self.base:
                new_exp = self.exp.extract_additively(c.exp)
                if new_exp is not None:
                    return self.base ** (new_exp)
            elif c == self.base:
                new_exp = self.exp.extract_additively(1)
                if new_exp is not None:
                    return self.base ** (new_exp)

    def extract_additively(self, c):
        """Return self - c if it's possible to subtract c from self and
        make all matching coefficients move towards zero, else return None.

        Examples
        ========

        >>> from sympy.abc import x, y
        >>> e = 2*x + 3
        >>> e.extract_additively(x + 1)
        x + 2
        >>> e.extract_additively(3*x)
        >>> e.extract_additively(4)
        >>> (y*(x + 1)).extract_additively(x + 1)
        >>> ((x + 1)*(x + 2*y + 1) + 3).extract_additively(x + 1)
        (x + 1)*(x + 2*y) + 3

        Sometimes auto-expansion will return a less simplified result
        than desired; gcd_terms might be used in such cases:

        >>> from sympy import gcd_terms
        >>> (4*x*(y + 1) + y).extract_additively(x)
        4*x*(y + 1) + x*(4*y + 3) - x*(4*y + 4) + y
        >>> gcd_terms(_)
        x*(4*y + 3) + y

        See Also
        ========
        extract_multiplicatively
        coeff
        as_coefficient

        """

        c = sympify(c)
        if self is S.NaN:
            return None
        if c is S.Zero:
            return self
        elif c == self:
            return S.Zero
 
 S.Zero:
            return self
        elif c == self:
            return S.Zero
 
