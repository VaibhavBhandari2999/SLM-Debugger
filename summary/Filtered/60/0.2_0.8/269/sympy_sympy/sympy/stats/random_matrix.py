from __future__ import print_function, division

from sympy import Basic
from sympy.stats.rv import PSpace, _symbol_converter, RandomMatrixSymbol

class RandomMatrixPSpace(PSpace):
    """
    Represents probability space for
    random matrices. It contains the mechanics
    for handling the API calls for random matrices.
    """
    def __new__(cls, sym, model=None):
        sym = _symbol_converter(sym)
        return Basic.__new__(cls, sym, model)

    model = property(lambda self: self.args[1])

    def compute_density(self, expr, *args):
        """
        Compute the density of a given random matrix expression.
        
        This function calculates the density of a random matrix expression. It supports expressions containing at most one `RandomMatrixSymbol` object. If the expression contains more than one `RandomMatrixSymbol` or is not a `RandomMatrixSymbol`, the function raises a `NotImplementedError`.
        
        Parameters:
        expr (RandomMatrixSymbol): The random matrix expression for which the density is to be computed.
        *args: Additional arguments (currently not used).
        
        Returns:
        """

        rms = expr.atoms(RandomMatrixSymbol)
        if len(rms) > 2 or (not isinstance(expr, RandomMatrixSymbol)):
            raise NotImplementedError("Currently, no algorithm has been "
                    "implemented to handle general expressions containing "
                    "multiple random matrices.")
        return self.model.density(expr)
