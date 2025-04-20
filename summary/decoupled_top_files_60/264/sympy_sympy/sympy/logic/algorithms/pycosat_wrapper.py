from __future__ import print_function, division

from sympy.assumptions.cnf import EncodedCNF


def pycosat_satisfiable(expr, all_models=False):
    """
    Solve a Boolean satisfiability problem using the pycosat library.
    
    This function takes a Boolean expression and determines if it is satisfiable.
    If `all_models` is set to `False`, it returns `True` if the expression is
    satisfiable and `False` otherwise. If `all_models` is `True`, it returns a
    generator that yields all satisfying assignments.
    
    Parameters:
    expr (EncodedCNF or Expr): The Boolean expression to solve. If `expr`
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
            """
            Generate a sequence of solutions from a SAT solver.
            
            This generator function processes the results from a SAT solver and yields solutions. If the solver finds a solution, it yields a dictionary mapping variables to their truth values. If no solutions are found, it yields `False`.
            
            Parameters:
            results (iterable): An iterable of solutions from a SAT solver. Each element in the iterable is a list of literals representing a solution.
            
            Yields:
            dict or bool: A dictionary mapping variables to their truth values if a
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
