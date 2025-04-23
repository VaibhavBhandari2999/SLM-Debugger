from sympy.assumptions.cnf import EncodedCNF


def pycosat_satisfiable(expr, all_models=False):
    """
    Solve a Boolean satisfiability problem using the pycosat library.
    
    This function checks if a given Boolean expression is satisfiable. It can also generate all possible models (satisfying assignments) for the expression.
    
    Parameters:
    expr (EncodedCNF or Expr): The Boolean expression to be checked for satisfiability. If an Expr is provided, it is first converted to an EncodedCNF.
    all_models (bool, optional): If True, the function returns a generator yielding all
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
            """
            Generate a sequence of solutions or a final result from a SAT solver.
            
            This generator function processes the results from a SAT solver. It yields a sequence of solutions, where each solution is a dictionary mapping variables to their truth values. If no solutions are found, it yields `False`.
            
            Parameters:
            results (iterable): An iterable that yields solutions from a SAT solver. Each solution is expected to be an iterable of literals.
            
            Yields:
            dict or bool: A dictionary representing a solution where keys are variable
            """

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
