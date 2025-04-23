from __future__ import print_function, division

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
        return dict((expr.symbols[abs(lit) - 1], lit > 0) for lit in r)
    else:
        r = pycosat.itersolve(expr.data)
        result = (r != "UNSAT")
        if not result:
            return result

        # Make solutions sympy compatible by creating a generator
        def _gen(results):
            """
            Generate a sequence of solutions from a SAT solver.
            
            This generator function yields solutions to a satisfiability problem. It processes the results from a SAT solver and returns each solution as a dictionary mapping variables to their truth values. If no solutions are found, it yields `False`.
            
            Parameters:
            results (iterator): An iterator that yields solutions from a SAT solver.
            
            Yields:
            dict or bool: A dictionary mapping variable indices to their truth values (True or False), or `False` if no solutions are found
            """

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
