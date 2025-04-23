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
        Simplify the input expression using the `cosm1` function.
        
        This function simplifies the input expression `x` and then applies the `cosm1` function to the simplified expression. If the simplified expression is not equal to the original `cosm1` expression with evaluation disabled, the simplified version is returned. Otherwise, the original `cosm1` expression is returned.
        
        Parameters:
        x (Expression): The input expression to be simplified and processed.
        
        Keyword Arguments:
        **kwargs
        """

        candidate = _cosm1(x.simplify(**kwargs))
        if candidate != _cosm1(x, evaluate=False):
            return candidate
        else:
            return cosm1(x)
