from __future__ import print_function, division

from sympy.core.decorators import wraps


def recurrence_memo(initial):
    """
    Memo decorator for sequences defined by recurrence

    See usage examples e.g. in the specfun/combinatorial module
    """
    cache = initial

    def decorator(f):
        """
        Decorator function that caches the results of a function to optimize repeated calls.
        
        This function takes a function `f` as input and returns a new function `g`. The new function `g` will cache the results of `f` for each unique input `n` to avoid redundant computations. The cache is stored in a list `cache` which is maintained within the scope of `g`.
        
        Parameters:
        f (function): The function to be decorated and optimized with caching.
        
        Returns:
        function:
        """

        @wraps(f)
        def g(n):
            """
            Generates a sequence value based on a recursive function.
            
            This function calculates the n-th element of a sequence using a recursive function `f` and stores intermediate results in a cache list to optimize repeated calls.
            
            Parameters:
            n (int): The index of the sequence element to compute.
            
            Returns:
            int: The n-th element of the sequence.
            
            Keywords:
            cache (list): A list used to store previously computed values to avoid redundant calculations.
            """

            L = len(cache)
            if n <= L - 1:
                return cache[n]
            for i in range(L, n + 1):
                cache.append(f(i, cache))
            return cache[-1]
        return g
    return decorator


def assoc_recurrence_memo(base_seq):
    """
    Memo decorator for associated sequences defined by recurrence starting from base

    base_seq(n) -- callable to get base sequence elements

    XXX works only for Pn0 = base_seq(0) cases
    XXX works only for m <= n cases
    """

    cache = []

    def decorator(f):
        @wraps(f)
        def g(n, m):
            L = len(cache)
            if n < L:
                return cache[n][m]

            for i in range(L, n + 1):
                # get base sequence
                F_i0 = base_seq(i)
                F_i_cache = [F_i0]
                cache.append(F_i_cache)

                # XXX only works for m <= n cases
                # generate assoc sequence
                for j in range(1, i + 1):
                    F_ij = f(i, j, cache)
                    F_i_cache.append(F_ij)

            return cache[n][m]

        return g
    return decorator
