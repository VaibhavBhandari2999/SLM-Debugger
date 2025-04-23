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
            Generate a sequence of solutions or a boolean indicating unsatisfiability.
            
            This generator function yields solutions to a satisfiability problem or returns False if no solution exists.
            
            Parameters:
            results (iterator): An iterator that provides solutions to the satisfiability problem.
            
            Yields:
            dict or bool: A dictionary mapping variables to their truth values if a solution is found, or False if no solution exists.
            
            Key Points:
            - The function uses a generator to yield solutions one by one.
            - It sets a flag `satisf
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
