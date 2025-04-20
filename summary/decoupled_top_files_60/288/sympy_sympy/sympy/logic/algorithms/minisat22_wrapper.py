from sympy.assumptions.cnf import EncodedCNF

def minisat22_satisfiable(expr, all_models=False, minimal=False):
    """
    Determines the satisfiability of a given logical expression using the Minisat22 solver.
    
    This function checks if a logical expression is satisfiable using the Minisat22 solver. It can also generate all possible models (satisfying assignments) and ensure the models are minimal.
    
    Parameters:
    expr (EncodedCNF or Expr): The logical expression to be checked for satisfiability. If an Expr is provided, it is first converted to an EncodedCNF.
    all_models (
    """


    if not isinstance(expr, EncodedCNF):
        exprs = EncodedCNF()
        exprs.add_prop(expr)
        expr = exprs

    from pysat.solvers import Minisat22

    # Return UNSAT when False (encoded as 0) is present in the CNF
    if {0} in expr.data:
        if all_models:
            return (f for f in [False])
        return False

    r = Minisat22(expr.data)

    if minimal:
        r.set_phases([-(i+1) for i in range(r.nof_vars())])

    if not r.solve():
        return False

    if not all_models:
        return {expr.symbols[abs(lit) - 1]: lit > 0 for lit in r.get_model()}

    else:
        # Make solutions sympy compatible by creating a generator
        def _gen(results):
            """
            Generate a sequence of solutions for a SAT problem.
            
            This function yields solutions for a SAT (Boolean satisfiability) problem using a solver. It can generate minimal solutions by adding clauses to the solver to avoid previously found solutions.
            
            Parameters:
            - results (Solver): A SAT solver instance that has been initialized with the problem constraints.
            
            Keywords:
            - minimal (bool): If True, the function will generate minimal solutions by adding clauses to the solver to avoid previously found solutions. Default is False.
            
            Yields:
            -
            """

            satisfiable = False
            while results.solve():
                sol = results.get_model()
                yield {expr.symbols[abs(lit) - 1]: lit > 0 for lit in sol}
                if minimal:
                    results.add_clause([-i for i in sol if i>0])
                else:
                    results.add_clause([-i for i in sol])
                satisfiable = True
            if not satisfiable:
                yield False
            raise StopIteration


        return _gen(r)
