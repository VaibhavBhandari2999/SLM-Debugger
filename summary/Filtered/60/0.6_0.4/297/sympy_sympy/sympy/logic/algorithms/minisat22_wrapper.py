from sympy.assumptions.cnf import EncodedCNF

def minisat22_satisfiable(expr, all_models=False, minimal=False):
    """
    Determines the satisfiability of a given logical expression using the Minisat22 solver.
    
    This function takes a logical expression and determines whether it is satisfiable. It can also generate all possible models (satisfying assignments) for the expression. Additionally, it can find minimal models if specified.
    
    Parameters:
    expr (EncodedCNF or Expr): The logical expression to be checked for satisfiability. If an Expr is provided, it is first converted to an EncodedCNF.
    all
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
        # Make solutions SymPy compatible by creating a generator
        def _gen(results):
            """
            Generate a sequence of solutions for a satisfiability problem.
            
            This function yields solutions for a satisfiability problem using a solver. It continues to find and yield solutions until no more solutions are possible. If the `minimal` flag is set to True, it attempts to find minimal solutions by adding clauses to the solver to prevent previously found solutions from being found again.
            
            Parameters:
            results (Solver): An instance of a SAT solver that has a `solve` method and a `get_model` method.
            
            Keyword
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
