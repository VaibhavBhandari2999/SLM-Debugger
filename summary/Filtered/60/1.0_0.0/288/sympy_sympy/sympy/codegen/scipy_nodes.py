from sympy.core.function import Add, ArgumentIndexError, Function
from sympy.core.singleton import S
from sympy.functions.elementary.trigonometric import cos, sin


def _cosm1(x, *, evaluate=True):
    return Add(cos(x, evaluate=evaluate), -S.One, evaluate=evaluate)


class cosm1(Function):
    """ Minus one plus cosine of x, i.e. cos(x) - 1. For use when x is close to zero.

    Helper class for use with e.g. scipy.special.cosm1
    See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.cosm1.html
    """
    nargs = 1

    def fdiff(self, argindex=1):
        """
        Returns the first derivative of this function.
        """
        if argindex == 1:
            return -sin(*self.args)
        else:
            raise ArgumentIndexError(self, argindex)

    def _eval_rewrite_as_cos(self, x, **kwargs):
        return _cosm1(x)

    def _eval_evalf(self, *args, **kwargs):
        return self.rewrite(cos).evalf(*args, **kwargs)

    def _eval_simplify(self, x, **kwargs):
        """
        Evaluates and simplifies the hyperbolic cosine minus one function.
        
        This function simplifies the input expression `x` using the `simplify` method and then checks if the simplified expression is different from the original expression wrapped in `cosm1`. If the simplified expression is different, it returns the simplified version; otherwise, it returns the original `cosm1` expression.
        
        Parameters:
        x (Expression): The input expression to be simplified and evaluated.
        
        Keyword Arguments:
        **kwargs
        """

        candidate = _cosm1(x.simplify(**kwargs))
        if candidate != _cosm1(x, evaluate=False):
            return candidate
        else:
            return cosm1(x)
