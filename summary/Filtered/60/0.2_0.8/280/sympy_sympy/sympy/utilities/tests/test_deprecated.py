from sympy.testing.pytest import warns_deprecated_sympy, XFAIL

# See https://github.com/sympy/sympy/pull/18095

def test_deprecated_utilities():
    """
    Tests for deprecated utilities in SymPy.
    
    This function checks for deprecated utilities in SymPy and issues warnings when they are imported.
    
    Key Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses the `warns_deprecated_sympy` context manager to issue warnings for deprecated utilities.
    - Deprecated utilities include `sympy.utilities.pytest`, `sympy.utilities.runtests`, `sympy.utilities.randtest`, `sympy.utilities.tmpfiles`, and `sympy
    """

    with warns_deprecated_sympy():
        import sympy.utilities.pytest  # noqa:F401
    with warns_deprecated_sympy():
        import sympy.utilities.runtests  # noqa:F401
    with warns_deprecated_sympy():
        import sympy.utilities.randtest  # noqa:F401
    with warns_deprecated_sympy():
        import sympy.utilities.tmpfiles  # noqa:F401
    with warns_deprecated_sympy():
        import sympy.utilities.quality_unicode  # noqa:F401

# This fails because benchmarking isn't importable...
@XFAIL
def test_deprecated_benchmarking():
    with warns_deprecated_sympy():
        import sympy.utilities.benchmarking  # noqa:F401
