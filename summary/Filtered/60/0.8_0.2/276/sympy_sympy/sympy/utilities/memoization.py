from sympy.core.decorators import wraps


def recurrence_memo(initial):
    """
    Memo decorator for sequences defined by recurrence

    See usage examples e.g. in the specfun/combinatorial module
    """
    cache = initial

    def decorator(f):
        """
        Decorator function to memoize the results of a function f that takes two integer arguments n and m. The function f is expected to compute a value based on n and m, and the decorator caches these results to avoid redundant computations. The decorator maintains a cache of computed values, where cache[n] is a list of computed values for each m up to n. The function base_seq(i) is a helper function that computes the base sequence for a given i, and f(i, j, cache)
        """

        @wraps(f)
        def g(n):
            """
            Generate the n-th element of a sequence using memoization.
            
            Parameters:
            n (int): The position in the sequence for which the value is to be computed.
            
            Returns:
            int: The n-th element of the sequence.
            
            This function uses memoization to store previously computed values in a cache list to avoid redundant calculations. If the requested index is within the bounds of the existing cache, the cached value is returned. Otherwise, the function computes the value for each index from the last cached element up
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
