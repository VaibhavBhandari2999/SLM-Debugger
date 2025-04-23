from __future__ import print_function, division

from sympy.assumptions.cnf import EncodedCNF


def pycosat_satisfiable(expr, all_models=False):
    """
    Solve a Boolean satisfiability problem using the pycosat library.
    
    This function attempts to find a satisfying assignment for a given Boolean
    expression. The expression can be a single Boolean formula or a collection
    of formulas.
    
    Parameters:
    expr (EncodedCNF or Expr): The Boolean expression to solve. If it is an
    Expr, it will be converted to an EncodedCNF.
    all_models (bool, optional): If True, return all satisfying models. If
    """

    import pycosat
    if not isinstance(expr, EncodedCNF):
        exprs = EncodedCNF()
        exprs.add_prop(expr)
        expr = exprs

    # Return UNSAT when False (encoded as 0) is present in the CNF
    if {0} in expr.data:
        if all_models:
            return (f for f in [False])
        return False

    if not all_models:
        r = pycosat.solve(expr.data)
        result = (r != "UNSAT")
        if not result:
            return result
        return dict((expr.symbols[abs(lit) - 1], lit > 0) for lit in r)
    else:
        r = pycosat.itersolve(expr.data)
        result = (r != "UNSAT")
        if not result:
            return result

        # Make solutions sympy compatible by creating a generator
        def _gen(results):
            satisfiable = False
            try:
                while True:
                    sol = next(results)
                    yield dict((expr.symbols[abs(lit) - 1], lit > 0) for lit in sol)
                    satisfiable = True
            except StopIteration:
                if not satisfiable:
                    yield False

        return _gen(r)
0) for lit in sol)
                    satisfiable = True
            except StopIteration:
                if not satisfiable:
                    yield False

        return _gen(r)
