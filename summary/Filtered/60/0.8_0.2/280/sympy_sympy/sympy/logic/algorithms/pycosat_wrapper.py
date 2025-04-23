from sympy.assumptions.cnf import EncodedCNF


def pycosat_satisfiable(expr, all_models=False):
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
            Generate a sequence of solutions from a SAT solver.
            
            This generator function processes the results from a SAT solver and yields solutions. If the solver finds a solution, it yields a dictionary mapping variables to their truth values. If no solutions are found, it yields `False`.
            
            Parameters:
            results (iterable): An iterable that yields solutions from a SAT solver. Each solution is expected to be an iterable of literals.
            
            Yields:
            dict or bool: A dictionary mapping variable symbols to their truth values if a solution
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
