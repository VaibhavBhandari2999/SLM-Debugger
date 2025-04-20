from sympy.core.decorators import wraps


def recurrence_memo(initial):
    """
    Memo decorator for sequences defined by recurrence

    See usage examples e.g. in the specfun/combinatorial module
    """
    cache = initial

    def decorator(f):
        """
        Decorator for memoizing a function that calculates a sequence of numbers (F_i0, F_i1, ..., F_in) for a given n. The function f(i, j, cache) is used to generate the j-th term of the sequence for a given i. The decorator maintains a cache of previously computed sequences to avoid redundant calculations. The function g(n, m) returns the m-th term of the sequence for the given n.
        
        Parameters:
        - f: A function that takes three arguments
        """

        @wraps(f)
        def g(n):
            """
            Generate the m-th element of the n-th sequence in a series of integer sequences.
            
            This function calculates the m-th element of the n-th sequence in a series of integer sequences. The sequences are generated based on a base sequence and a function `f` that computes the elements of the associated sequence.
            
            Parameters:
            n (int): The index of the sequence in the series.
            m (int): The index of the element in the sequence to be computed.
            
            Returns:
            int: The m
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
