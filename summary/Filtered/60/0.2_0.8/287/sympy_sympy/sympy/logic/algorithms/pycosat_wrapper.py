from sympy.assumptions.cnf import EncodedCNF


def pycosat_satisfiable(expr, all_models=False):
    """
    Solve a propositional logic expression for satisfiability using the pycosat solver.
    
    This function takes a propositional logic expression and determines if it is satisfiable. It can also return all possible models (satisfying assignments) for the expression.
    
    Parameters:
    expr (EncodedCNF or Expr): The propositional logic expression to be solved. If an Expr is provided, it is first converted to an EncodedCNF.
    all_models (bool, optional): If True, the
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
        return {expr.symbols[abs(lit) - 1]: lit > 0 for lit in r}
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
                    yield {expr.symbols[abs(lit) - 1]: lit > 0 for lit in sol}
                    satisfiable = True
            except StopIteration:
                if not satisfiable:
                    yield False

        return _gen(r)
