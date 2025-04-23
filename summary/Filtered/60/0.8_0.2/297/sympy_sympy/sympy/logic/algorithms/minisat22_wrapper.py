from sympy.assumptions.cnf import EncodedCNF

def minisat22_satisfiable(expr, all_models=False, minimal=False):
    """
    Determines if a given propositional logic expression is satisfiable using the Minisat22 solver.
    
    This function takes a propositional logic expression and checks if it is satisfiable. It can also generate all possible models (satisfying assignments) and find minimal models.
    
    Parameters:
    expr (Expr or EncodedCNF): The propositional logic expression to be checked. If it is not already an EncodedCNF, it will be converted.
    all_models (bool, optional):
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
            Generate a sequence of solutions to a Boolean satisfiability problem.
            
            This function is used to find and yield solutions to a Boolean satisfiability problem. It iteratively solves the problem and returns a sequence of solutions. If the `minimal` flag is set, it attempts to find minimal solutions by adding clauses to the problem instance.
            
            Parameters:
            results (pysat.Solver): A PySAT solver instance that contains the Boolean satisfiability problem.
            
            Keywords:
            minimal (bool): If True, the
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
