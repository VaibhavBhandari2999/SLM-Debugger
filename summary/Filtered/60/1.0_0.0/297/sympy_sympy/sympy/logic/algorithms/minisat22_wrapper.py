from sympy.assumptions.cnf import EncodedCNF

def minisat22_satisfiable(expr, all_models=False, minimal=False):
    """
    Solve a Boolean satisfiability problem using the Minisat22 solver.
    
    This function takes a Boolean expression and determines if it is satisfiable. It can also generate all possible models (satisfying assignments) and ensure the models are minimal.
    
    Parameters:
    expr (EncodedCNF or Expr): The Boolean expression to be solved. It can be an instance of EncodedCNF or any other Expr that can be encoded into CNF.
    all_models (bool, optional): If True
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
            
            This function yields solutions to a satisfiability problem using a solver. It can generate minimal solutions by adding clauses to avoid previously found solutions.
            
            Parameters:
            results (Solver): An instance of a SAT solver that has a `solve` method and a `get_model` method.
            minimal (bool, optional): If True, the function will generate minimal solutions by adding clauses to the solver to avoid previously found solutions. Defaults to False.
            
            Yields:
            dict
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
