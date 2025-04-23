from sympy.assumptions.cnf import EncodedCNF

def minisat22_satisfiable(expr, all_models=False, minimal=False):
    """
    Determines if a given propositional logic expression is satisfiable using the Minisat22 solver.
    
    This function takes a propositional logic expression and checks if it is satisfiable. It can also generate all possible models (satisfying assignments) and ensure that the models are minimal.
    
    Parameters:
    expr (EncodedCNF or Expr): The propositional logic expression to check for satisfiability. If an Expr is provided, it is first converted to an EncodedCNF.
    all_models
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
            
            This function yields solutions to a SAT (Boolean satisfiability) problem. It continuously solves the problem and generates solutions until no more solutions are found.
            
            Parameters:
            results (pysat.Solver): A SAT solver instance from the pysat library that contains the problem to be solved.
            
            Keyword Arguments:
            minimal (bool): If True, only the minimal subset of literals that make the formula true is added as a clause to the solver. If False, all
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
