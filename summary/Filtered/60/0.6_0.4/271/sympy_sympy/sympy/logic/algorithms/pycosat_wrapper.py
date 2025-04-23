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
            Generate a sequence of solutions or a final state from a results iterator.
            
            This function processes an iterator `results` that yields solutions to a logical problem. It generates a sequence of dictionaries representing the solutions, where each dictionary maps a variable to its truth value. If the iterator is exhausted without finding any solutions, it returns `False`.
            
            Parameters:
            results (iterator): An iterator that yields solutions as lists of literals.
            
            Yields:
            dict or bool: A dictionary mapping variables to their truth values if
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
