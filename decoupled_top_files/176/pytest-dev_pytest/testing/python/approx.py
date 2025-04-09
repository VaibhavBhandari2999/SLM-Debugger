import operator
from decimal import Decimal
from fractions import Fraction
from operator import eq
from operator import ne

import pytest
from pytest import approx

inf, nan = float("inf"), float("nan")


@pytest.fixture
def mocked_doctest_runner(monkeypatch):
    """
    mocked_doctest_runner is a function that takes a monkeypatch object as an argument and returns a custom DocTestRunner object.
    
    Args:
    monkeypatch (object): A monkeypatch object used to replace the _OutputRedirectingPdb class with a MockedPdb class in the doctest module.
    
    Returns:
    MyDocTestRunner: A custom DocTestRunner object that raises an AssertionError if a test fails, indicating that the evaluated result does not match the expected output.
    """

    import doctest

    class MockedPdb:
        def __init__(self, out):
            pass

        def set_trace(self):
            raise NotImplementedError("not used")

        def reset(self):
            pass

        def set_continue(self):
            pass

    monkeypatch.setattr("doctest._OutputRedirectingPdb", MockedPdb)

    class MyDocTestRunner(doctest.DocTestRunner):
        def report_failure(self, out, test, example, got):
            """
            Generates an assertion error message when a test fails.
            
            Args:
            out (str): The output of the evaluated expression.
            test (str): The name or description of the test case.
            example (Example): An object containing the source code, expected output, and actual output of the test case.
            got (str): The actual output of the evaluated expression.
            
            Raises:
            AssertionError: If the evaluated expression does not match the expected output.
            
            Summary:
            This function raises
            """

            raise AssertionError(
                "'{}' evaluates to '{}', not '{}'".format(
                    example.source.strip(), got.strip(), example.want.strip()
                )
            )

    return MyDocTestRunner()


class TestApprox:
    def test_repr_string(self):
        """
        Test the representation of approx objects.
        
        This function tests various representations of approx objects, including:
        - Floating point numbers
        - Lists
        - Tuples
        - Infinite values
        - NaN relative tolerance
        - Infinite relative tolerance
        - Dictionaries (unordered)
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any of the expected representations do not match the actual output.
        """

        assert repr(approx(1.0)) == "1.0 ± 1.0e-06"
        assert repr(approx([1.0, 2.0])) == "approx([1.0 ± 1.0e-06, 2.0 ± 2.0e-06])"
        assert repr(approx((1.0, 2.0))) == "approx((1.0 ± 1.0e-06, 2.0 ± 2.0e-06))"
        assert repr(approx(inf)) == "inf"
        assert repr(approx(1.0, rel=nan)) == "1.0 ± ???"
        assert repr(approx(1.0, rel=inf)) == "1.0 ± inf"

        # Dictionaries aren't ordered, so we need to check both orders.
        assert repr(approx({"a": 1.0, "b": 2.0})) in (
            "approx({'a': 1.0 ± 1.0e-06, 'b': 2.0 ± 2.0e-06})",
            "approx({'b': 2.0 ± 2.0e-06, 'a': 1.0 ± 1.0e-06})",
        )

    def test_repr_complex_numbers(self):
        """
        Test the representation of complex numbers using the `approx` function.
        
        - `approx`: A function that approximates a given complex number with a specified relative or absolute tolerance.
        - Input: Complex numbers with various tolerances.
        - Output: String representations of the approximated complex numbers, including their magnitude and angle tolerance.
        """

        assert repr(approx(inf + 1j)) == "(inf+1j)"
        assert repr(approx(1.0j, rel=inf)) == "1j ± inf"

        # can't compute a sensible tolerance
        assert repr(approx(nan + 1j)) == "(nan+1j) ± ???"

        assert repr(approx(1.0j)) == "1j ± 1.0e-06 ∠ ±180°"

        # relative tolerance is scaled to |3+4j| = 5
        assert repr(approx(3 + 4 * 1j)) == "(3+4j) ± 5.0e-06 ∠ ±180°"

        # absolute tolerance is not scaled
        assert repr(approx(3.3 + 4.4 * 1j, abs=0.02)) == "(3.3+4.4j) ± 2.0e-02 ∠ ±180°"

    @pytest.mark.parametrize(
        "value, expected_repr_string",
        [
            (5.0, "approx(5.0 ± 5.0e-06)"),
            ([5.0], "approx([5.0 ± 5.0e-06])"),
            ([[5.0]], "approx([[5.0 ± 5.0e-06]])"),
            ([[5.0, 6.0]], "approx([[5.0 ± 5.0e-06, 6.0 ± 6.0e-06]])"),
            ([[5.0], [6.0]], "approx([[5.0 ± 5.0e-06], [6.0 ± 6.0e-06]])"),
        ],
    )
    def test_repr_nd_array(self, value, expected_repr_string):
        """Make sure that arrays of all different dimensions are repr'd correctly."""
        np = pytest.importorskip("numpy")
        np_array = np.array(value)
        assert repr(approx(np_array)) == expected_repr_string

    def test_operator_overloading(self):
        """
        Tests operator overloading for approximate equality using the `approx` function.
        
        Args:
        None
        
        Returns:
        None
        
        Notes:
        - The `approx` function is used to compare floating-point numbers with a specified relative (`rel`) and absolute (`abs`) tolerance.
        - The tests check for both equality and inequality using the `==` and `!=` operators.
        - The `assert` statements are used to validate the results of the comparisons.
        """

        assert 1 == approx(1, rel=1e-6, abs=1e-12)
        assert not (1 != approx(1, rel=1e-6, abs=1e-12))
        assert 10 != approx(1, rel=1e-6, abs=1e-12)
        assert not (10 == approx(1, rel=1e-6, abs=1e-12))

    def test_exactly_equal(self):
        """
        Test that two values are exactly equal using the `==` operator.
        
        Args:
        a (float, int, Decimal, Fraction): The first value to compare.
        x (float, int, Decimal, Fraction): The second value to compare.
        
        Returns:
        bool: True if `a` is exactly equal to `x`, False otherwise.
        
        Examples:
        >>> test_exactly_equal(2.0, 2.0)
        True
        >>> test_exactly_equal
        """

        examples = [
            (2.0, 2.0),
            (0.1e200, 0.1e200),
            (1.123e-300, 1.123e-300),
            (12345, 12345.0),
            (0.0, -0.0),
            (345678, 345678),
            (Decimal("1.0001"), Decimal("1.0001")),
            (Fraction(1, 3), Fraction(-1, -3)),
        ]
        for a, x in examples:
            assert a == approx(x)

    def test_opposite_sign(self):
        """
        Test if two numbers have opposite signs.
        
        Args:
        op (function): The comparison operator to use (e.g., `eq` for equality).
        a (float): The first number to compare.
        x (float): The second number to compare, with an approximate value of -a.
        
        Returns:
        None: This function asserts that the given operator returns True when comparing `a` and its approximate negative `-1e-100`.
        """

        examples = [(eq, 1e-100, -1e-100), (ne, 1e100, -1e100)]
        for op, a, x in examples:
            assert op(a, approx(x))

    def test_zero_tolerance(self):
        """
        Test zero tolerance for approximate equality.
        
        This function checks how two numbers `a` and `x` are compared using
        the `approx` function with different relative (`rel`) and absolute
        (`abs`) tolerances. The inputs `a` and `x` are pairs of values
        that are very close to each other but not exactly equal due to
        floating-point precision issues.
        
        Args:
        None (The test is performed internally).
        
        Returns:
        None (
        """

        within_1e10 = [(1.1e-100, 1e-100), (-1.1e-100, -1e-100)]
        for a, x in within_1e10:
            assert x == approx(x, rel=0.0, abs=0.0)
            assert a != approx(x, rel=0.0, abs=0.0)
            assert a == approx(x, rel=0.0, abs=5e-101)
            assert a != approx(x, rel=0.0, abs=5e-102)
            assert a == approx(x, rel=5e-1, abs=0.0)
            assert a != approx(x, rel=5e-2, abs=0.0)

    def test_negative_tolerance(self):
        """
        Test negative tolerances.
        
        This function checks that negative tolerances are not allowed when using
        the `approx` function. It raises a `ValueError` for each set of invalid
        keyword arguments passed to the `approx` function.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If any of the provided keyword arguments have negative
        values for 'rel' or 'abs'.
        
        Keyword Arguments:
        rel (float): Relative tolerance.
        """

        # Negative tolerances are not allowed.
        illegal_kwargs = [
            dict(rel=-1e100),
            dict(abs=-1e100),
            dict(rel=1e100, abs=-1e100),
            dict(rel=-1e100, abs=1e100),
            dict(rel=-1e100, abs=-1e100),
        ]
        for kwargs in illegal_kwargs:
            with pytest.raises(ValueError):
                1.1 == approx(1, **kwargs)

    def test_inf_tolerance(self):
        """
        Tests the `approx` function with various inputs and inf tolerance values.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `approx`: Compares two values with given relative and absolute tolerances.
        - `assert`: Verifies that the comparison results are as expected.
        
        Key Variables:
        - `large_diffs`: A list of tuples containing pairs of numbers with significant differences.
        """

        # Everything should be equal if the tolerance is infinite.
        large_diffs = [(1, 1000), (1e-50, 1e50), (-1.0, -1e300), (0.0, 10)]
        for a, x in large_diffs:
            assert a != approx(x, rel=0.0, abs=0.0)
            assert a == approx(x, rel=inf, abs=0.0)
            assert a == approx(x, rel=0.0, abs=inf)
            assert a == approx(x, rel=inf, abs=inf)

    def test_inf_tolerance_expecting_zero(self):
        """
        Test the inf tolerance with expecting zero.
        
        This function checks if the relative tolerance is zero and the expected
        value is infinite, resulting in a NaN actual tolerance, which should raise
        a ValueError. The function uses the `approx` function from the `pytest`
        library to perform the comparison.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the relative tolerance is zero and the expected value
        is infinite, the function raises a ValueError
        """

        # If the relative tolerance is zero but the expected value is infinite,
        # the actual tolerance is a NaN, which should be an error.
        illegal_kwargs = [dict(rel=inf, abs=0.0), dict(rel=inf, abs=inf)]
        for kwargs in illegal_kwargs:
            with pytest.raises(ValueError):
                1 == approx(0, **kwargs)

    def test_nan_tolerance(self):
        """
        Test the tolerance of NaN values in the `approx` function.
        
        This function checks that the `approx` function raises a `ValueError`
        when invalid keyword arguments containing NaN (`nan`) are passed. The
        invalid keyword arguments tested include 'rel' (relative tolerance) and
        'abs' (absolute tolerance), both individually and in combination.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If any of the invalid keyword arguments are passed
        """

        illegal_kwargs = [dict(rel=nan), dict(abs=nan), dict(rel=nan, abs=nan)]
        for kwargs in illegal_kwargs:
            with pytest.raises(ValueError):
                1.1 == approx(1, **kwargs)

    def test_reasonable_defaults(self):
        """
        Asserts that the sum of 0.1 and 0.2 is approximately equal to 0.3 using the `approx` function to handle floating-point precision errors.
        
        - **Function:** `approx`
        - **Inputs:**
        - `0.1 + 0.2`: The sum of two floating-point numbers.
        - **Outputs:**
        - `True` if the approximation holds within a reasonable tolerance; otherwise, `False`.
        """

        # Whatever the defaults are, they should work for numbers close to 1
        # than have a small amount of floating-point error.
        assert 0.1 + 0.2 == approx(0.3)

    def test_default_tolerances(self):
        """
        Tests the default tolerances used in the `approx` function.
        
        This function checks that the default relative and absolute tolerances
        correctly determine whether two values are considered approximately equal.
        The `approx` function is used to compare the values `a` and `x` with the
        specified tolerances.
        
        Args:
        None
        
        Returns:
        None
        
        Examples:
        - Tests the relative tolerance for large numbers.
        - Tests the relative tolerance for small numbers.
        """

        # This tests the defaults as they are currently set.  If you change the
        # defaults, this test will fail but you should feel free to change it.
        # None of the other tests (except the doctests) should be affected by
        # the choice of defaults.
        examples = [
            # Relative tolerance used.
            (eq, 1e100 + 1e94, 1e100),
            (ne, 1e100 + 2e94, 1e100),
            (eq, 1e0 + 1e-6, 1e0),
            (ne, 1e0 + 2e-6, 1e0),
            # Absolute tolerance used.
            (eq, 1e-100, +1e-106),
            (eq, 1e-100, +2e-106),
            (eq, 1e-100, 0),
        ]
        for op, a, x in examples:
            assert op(a, approx(x))

    def test_custom_tolerances(self):
        """
        Asserts the equality of floating-point numbers with specified relative (rel) and absolute (abs) tolerances using the `approx` function.
        
        - `rel`: Relative tolerance.
        - `abs`: Absolute tolerance.
        
        Examples:
        >>> test_custom_tolerances()
        - Tests the equality of large numbers with different relative and absolute tolerances.
        - Tests the equality of small numbers with different relative and absolute tolerances.
        - Tests the equality of very small numbers with different relative and
        """

        assert 1e8 + 1e0 == approx(1e8, rel=5e-8, abs=5e0)
        assert 1e8 + 1e0 == approx(1e8, rel=5e-9, abs=5e0)
        assert 1e8 + 1e0 == approx(1e8, rel=5e-8, abs=5e-1)
        assert 1e8 + 1e0 != approx(1e8, rel=5e-9, abs=5e-1)

        assert 1e0 + 1e-8 == approx(1e0, rel=5e-8, abs=5e-8)
        assert 1e0 + 1e-8 == approx(1e0, rel=5e-9, abs=5e-8)
        assert 1e0 + 1e-8 == approx(1e0, rel=5e-8, abs=5e-9)
        assert 1e0 + 1e-8 != approx(1e0, rel=5e-9, abs=5e-9)

        assert 1e-8 + 1e-16 == approx(1e-8, rel=5e-8, abs=5e-16)
        assert 1e-8 + 1e-16 == approx(1e-8, rel=5e-9, abs=5e-16)
        assert 1e-8 + 1e-16 == approx(1e-8, rel=5e-8, abs=5e-17)
        assert 1e-8 + 1e-16 != approx(1e-8, rel=5e-9, abs=5e-17)

    def test_relative_tolerance(self):
        """
        Test relative tolerance for approximate equality.
        
        This function checks if two numbers are approximately equal within a
        specified relative tolerance. It uses the `approx` function with both
        relative (`rel`) and absolute (`abs`) tolerances to compare pairs of
        numbers. The pairs tested include values close to powers of ten,
        specifically (1e8 + 1e0, 1e8), (1e0 + 1e-8, 1e0), and
        """

        within_1e8_rel = [(1e8 + 1e0, 1e8), (1e0 + 1e-8, 1e0), (1e-8 + 1e-16, 1e-8)]
        for a, x in within_1e8_rel:
            assert a == approx(x, rel=5e-8, abs=0.0)
            assert a != approx(x, rel=5e-9, abs=0.0)

    def test_absolute_tolerance(self):
        """
        Test absolute tolerance using the `approx` function.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the absolute tolerance of two values using the `approx` function with relative tolerance set to 0. It checks if the first value is approximately equal to the second value within an absolute tolerance of 5e-8 and not within an absolute tolerance of 5e-9. The test cases include values close to 1e8, 1e
        """

        within_1e8_abs = [(1e8 + 9e-9, 1e8), (1e0 + 9e-9, 1e0), (1e-8 + 9e-9, 1e-8)]
        for a, x in within_1e8_abs:
            assert a == approx(x, rel=0, abs=5e-8)
            assert a != approx(x, rel=0, abs=5e-9)

    def test_expecting_zero(self):
        """
        Tests the `approx` function with various inputs and operations to check if they are approximately equal to zero within specified relative and absolute tolerances.
        
        Args:
        None
        
        Returns:
        None
        
        Examples:
        - Tests if `ne(1e-6, 0.0)` is approximately true using `approx` with relative tolerance 0.0 and absolute tolerance 1e-12.
        - Tests if `ne(-1e-6, 0.0
        """

        examples = [
            (ne, 1e-6, 0.0),
            (ne, -1e-6, 0.0),
            (eq, 1e-12, 0.0),
            (eq, -1e-12, 0.0),
            (ne, 2e-12, 0.0),
            (ne, -2e-12, 0.0),
            (ne, inf, 0.0),
            (ne, nan, 0.0),
        ]
        for op, a, x in examples:
            assert op(a, approx(x, rel=0.0, abs=1e-12))
            assert op(a, approx(x, rel=1e-6, abs=1e-12))

    def test_expecting_inf(self):
        """
        Tests various comparisons between floating-point numbers, including infinity (`inf`), negative infinity (`-inf`), and NaN. The function uses the `approx` function to handle approximate equality.
        
        Args:
        None (The function is a test method and does not take any arguments).
        
        Returns:
        None (The function asserts conditions and does not return any value).
        
        Important Functions:
        - `eq`: Tests for equality.
        - `ne`: Tests for inequality.
        - `approx`:
        """

        examples = [
            (eq, inf, inf),
            (eq, -inf, -inf),
            (ne, inf, -inf),
            (ne, 0.0, inf),
            (ne, nan, inf),
        ]
        for op, a, x in examples:
            assert op(a, approx(x))

    def test_expecting_nan(self):
        """
        Tests equality and inequality operations with NaN values using the `approx` function.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the behavior of equality (`eq`) and inequality (`ne`) operations involving NaN values using the `approx` function. It checks if NaN is considered equal to itself and to other NaN values when `nan_ok=True`. The `eq` and `ne` functions are used to compare values, while the `approx` function is utilized
        """

        examples = [
            (eq, nan, nan),
            (eq, -nan, -nan),
            (eq, nan, -nan),
            (ne, 0.0, nan),
            (ne, inf, nan),
        ]
        for op, a, x in examples:
            # Nothing is equal to NaN by default.
            assert a != approx(x)

            # If ``nan_ok=True``, then NaN is equal to NaN.
            assert op(a, approx(x, nan_ok=True))

    def test_int(self):
        """
        Test integer equality with approximate comparison.
        
        This function checks if integers are approximately equal using the `approx` function with specified relative (`rel`) and absolute (`abs`) tolerances. It tests the following cases:
        - Positive and negative integers close to 1,000,000.
        - Comparisons with different relative tolerances (5e-6 and 5e-7).
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        -
        """

        within_1e6 = [(1000001, 1000000), (-1000001, -1000000)]
        for a, x in within_1e6:
            assert a == approx(x, rel=5e-6, abs=0)
            assert a != approx(x, rel=5e-7, abs=0)
            assert approx(x, rel=5e-6, abs=0) == a
            assert approx(x, rel=5e-7, abs=0) != a

    def test_decimal(self):
        """
        Test decimal approximation with specified relative and absolute tolerances.
        
        Args:
        None
        
        Returns:
        None
        
        Notes:
        - The function tests the `approx` function for decimal values within 1e-6.
        - It uses the `Decimal` class for precise arithmetic operations.
        - The `approx` function is used to compare decimal numbers with specified relative (`rel`) and absolute (`abs`) tolerances.
        - The test cases check equality and inequality of decimal numbers using
        """

        within_1e6 = [
            (Decimal("1.000001"), Decimal("1.0")),
            (Decimal("-1.000001"), Decimal("-1.0")),
        ]
        for a, x in within_1e6:
            assert a == approx(x)
            assert a == approx(x, rel=Decimal("5e-6"), abs=0)
            assert a != approx(x, rel=Decimal("5e-7"), abs=0)
            assert approx(x, rel=Decimal("5e-6"), abs=0) == a
            assert approx(x, rel=Decimal("5e-7"), abs=0) != a

    def test_fraction(self):
        """
        Test the equality of two fractions using the `approx` function with specified relative and absolute tolerances.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the equality of two fractions, `a` and `x`, by comparing them using the `approx` function with different relative and absolute tolerances. The `within_1e6` list contains pairs of fractions to be compared. The `approx` function is used to check if `a` is
        """

        within_1e6 = [
            (1 + Fraction(1, 1000000), Fraction(1)),
            (-1 - Fraction(-1, 1000000), Fraction(-1)),
        ]
        for a, x in within_1e6:
            assert a == approx(x, rel=5e-6, abs=0)
            assert a != approx(x, rel=5e-7, abs=0)
            assert approx(x, rel=5e-6, abs=0) == a
            assert approx(x, rel=5e-7, abs=0) != a

    def test_complex(self):
        """
        Test complex number approximation with specified relative and absolute tolerances.
        
        Args:
        None
        
        Returns:
        None
        
        Notes:
        - The function tests the `approx` function for complex numbers within a certain tolerance.
        - It uses the `within_1e6` list containing tuples of complex numbers and their approximations.
        - The `approx` function is used to compare the complex numbers with specified relative (`rel`) and absolute (`abs`) tolerances.
        - The test
        """

        within_1e6 = [
            (1.000001 + 1.0j, 1.0 + 1.0j),
            (1.0 + 1.000001j, 1.0 + 1.0j),
            (-1.000001 + 1.0j, -1.0 + 1.0j),
            (1.0 - 1.000001j, 1.0 - 1.0j),
        ]
        for a, x in within_1e6:
            assert a == approx(x, rel=5e-6, abs=0)
            assert a != approx(x, rel=5e-7, abs=0)
            assert approx(x, rel=5e-6, abs=0) == a
            assert approx(x, rel=5e-7, abs=0) != a

    def test_list(self):
        """
        Tests if the elements of `actual` list are approximately equal to the elements of `expected` list within specified relative (`rel`) and absolute (`abs`) tolerances.
        
        Args:
        self: The instance of the class containing this method.
        
        Returns:
        None: This function does not return anything but asserts the conditions.
        
        Important Functions:
        - `approx`: Compares two lists with given relative and absolute tolerances.
        
        Important Variables:
        - `actual`: A list
        """

        actual = [1 + 1e-7, 2 + 1e-8]
        expected = [1, 2]

        # Return false if any element is outside the tolerance.
        assert actual == approx(expected, rel=5e-7, abs=0)
        assert actual != approx(expected, rel=5e-8, abs=0)
        assert approx(expected, rel=5e-7, abs=0) == actual
        assert approx(expected, rel=5e-8, abs=0) != actual

    def test_list_wrong_len(self):
        assert [1, 2] != approx([1])
        assert [1, 2] != approx([1, 2, 3])

    def test_tuple(self):
        """
        Tests tuple equality with specified relative and absolute tolerances using the `approx` function.
        
        Args:
        None
        
        Returns:
        None
        
        Notes:
        - Compares two tuples: `actual` and `expected`.
        - Uses the `approx` function to check for approximate equality within given tolerances.
        - The `rel` parameter specifies the relative tolerance.
        - The `abs` parameter specifies the absolute tolerance.
        """

        actual = (1 + 1e-7, 2 + 1e-8)
        expected = (1, 2)

        # Return false if any element is outside the tolerance.
        assert actual == approx(expected, rel=5e-7, abs=0)
        assert actual != approx(expected, rel=5e-8, abs=0)
        assert approx(expected, rel=5e-7, abs=0) == actual
        assert approx(expected, rel=5e-8, abs=0) != actual

    def test_tuple_wrong_len(self):
        assert (1, 2) != approx((1,))
        assert (1, 2) != approx((1, 2, 3))

    def test_dict(self):
        """
        Test dictionary comparison with specified relative and absolute tolerances.
        
        Args:
        None
        
        Returns:
        None
        
        Notes:
        - Compares two dictionaries `actual` and `expected`.
        - Uses `approx` function from `pytest.approx` module for comparison.
        - Checks equality and inequality of dictionaries within given tolerances.
        - Tolerances are specified using `rel` (relative) and `abs` (absolute).
        """

        actual = {"a": 1 + 1e-7, "b": 2 + 1e-8}
        # Dictionaries became ordered in python3.6, so switch up the order here
        # to make sure it doesn't matter.
        expected = {"b": 2, "a": 1}

        # Return false if any element is outside the tolerance.
        assert actual == approx(expected, rel=5e-7, abs=0)
        assert actual != approx(expected, rel=5e-8, abs=0)
        assert approx(expected, rel=5e-7, abs=0) == actual
        assert approx(expected, rel=5e-8, abs=0) != actual

    def test_dict_wrong_len(self):
        """
        Assert that two dictionaries are not approximately equal based on their lengths.
        
        Args:
        None (The function uses hardcoded dictionaries as inputs).
        
        Returns:
        None (The function raises an AssertionError if the dictionaries are approximately equal based on their lengths).
        
        Raises:
        AssertionError: If the dictionaries have different lengths or if they have the same length but different keys or values.
        
        Important Functions:
        - `approx`: Used to compare the lengths of the dictionaries.
        
        Example Usage:
        >>> test_dict
        """

        assert {"a": 1, "b": 2} != approx({"a": 1})
        assert {"a": 1, "b": 2} != approx({"a": 1, "c": 2})
        assert {"a": 1, "b": 2} != approx({"a": 1, "b": 2, "c": 3})

    def test_numpy_array(self):
        """
        Test comparison of NumPy arrays using the `approx` function.
        
        This test checks the behavior of the `approx` function when comparing NumPy arrays
        with specified relative (`rel`) and absolute (`abs`) tolerances. It verifies that
        the function correctly identifies when elements are within the given tolerances and
        when they are not. The test also confirms that the `approx` function can handle
        comparisons between NumPy arrays and lists.
        
        Args:
        None (The
        """

        np = pytest.importorskip("numpy")

        actual = np.array([1 + 1e-7, 2 + 1e-8])
        expected = np.array([1, 2])

        # Return false if any element is outside the tolerance.
        assert actual == approx(expected, rel=5e-7, abs=0)
        assert actual != approx(expected, rel=5e-8, abs=0)
        assert approx(expected, rel=5e-7, abs=0) == expected
        assert approx(expected, rel=5e-8, abs=0) != actual

        # Should be able to compare lists with numpy arrays.
        assert list(actual) == approx(expected, rel=5e-7, abs=0)
        assert list(actual) != approx(expected, rel=5e-8, abs=0)
        assert actual == approx(list(expected), rel=5e-7, abs=0)
        assert actual != approx(list(expected), rel=5e-8, abs=0)

    def test_numpy_tolerance_args(self):
        """
        Check that numpy rel/abs args are handled correctly
        for comparison against an np.array
        Check both sides of the operator, hopefully it doesn't impact things.
        Test all permutations of where the approx and np.array() can show up
        """
        np = pytest.importorskip("numpy")
        expected = 100.0
        actual = 99.0
        abs_diff = expected - actual
        rel_diff = (expected - actual) / expected

        tests = [
            (eq, abs_diff, 0),
            (eq, 0, rel_diff),
            (ne, 0, rel_diff / 2.0),  # rel diff fail
            (ne, abs_diff / 2.0, 0),  # abs diff fail
        ]

        for op, _abs, _rel in tests:
            assert op(np.array(actual), approx(expected, abs=_abs, rel=_rel))  # a, b
            assert op(approx(expected, abs=_abs, rel=_rel), np.array(actual))  # b, a

            assert op(actual, approx(np.array(expected), abs=_abs, rel=_rel))  # a, b
            assert op(approx(np.array(expected), abs=_abs, rel=_rel), actual)  # b, a

            assert op(np.array(actual), approx(np.array(expected), abs=_abs, rel=_rel))
            assert op(approx(np.array(expected), abs=_abs, rel=_rel), np.array(actual))

    def test_numpy_expecting_nan(self):
        """
        Test numpy operations with NaN values.
        
        This function tests various numpy operations involving NaN values using the `approx` function. It checks for equality and inequality of NaN values with other numbers and arrays, with and without allowing NaNs.
        
        Parameters:
        None
        
        Returns:
        None
        
        Functions Used:
        - `pytest.importorskip("numpy")`: Import the numpy module.
        - `eq`: Equality comparison function.
        - `ne`: Inequality comparison function.
        - `
        """

        np = pytest.importorskip("numpy")
        examples = [
            (eq, nan, nan),
            (eq, -nan, -nan),
            (eq, nan, -nan),
            (ne, 0.0, nan),
            (ne, inf, nan),
        ]
        for op, a, x in examples:
            # Nothing is equal to NaN by default.
            assert np.array(a) != approx(x)
            assert a != approx(np.array(x))

            # If ``nan_ok=True``, then NaN is equal to NaN.
            assert op(np.array(a), approx(x, nan_ok=True))
            assert op(a, approx(np.array(x), nan_ok=True))

    def test_numpy_expecting_inf(self):
        """
        Tests the behavior of NumPy operations with special values like infinity, NaN, and zero using the `approx` function.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `pytest.importorskip("numpy")`: Imports NumPy if available.
        - `eq`: Equality comparison operator.
        - `ne`: Inequality comparison operator.
        - `inf`: Positive infinity value.
        - `-inf`: Negative infinity value.
        - `nan`: Not
        """

        np = pytest.importorskip("numpy")
        examples = [
            (eq, inf, inf),
            (eq, -inf, -inf),
            (ne, inf, -inf),
            (ne, 0.0, inf),
            (ne, nan, inf),
        ]
        for op, a, x in examples:
            assert op(np.array(a), approx(x))
            assert op(a, approx(np.array(x)))
            assert op(np.array(a), approx(np.array(x)))

    def test_numpy_array_wrong_shape(self):
        """
        Asserts that two NumPy arrays with different shapes are not approximately equal.
        
        This function uses the `pytest.importorskip` method to ensure that the NumPy package is available. It then creates two NumPy arrays: `a12` with shape (1, 2) and `a21` with shape (2, 1). The function checks if these arrays are not approximately equal using the `!=` operator and the `approx` function.
        
        Args:
        None
        """

        np = pytest.importorskip("numpy")

        a12 = np.array([[1, 2]])
        a21 = np.array([[1], [2]])

        assert a12 != approx(a21)
        assert a21 != approx(a12)

    def test_doctests(self, mocked_doctest_runner):
        """
        Run doctests for the `approx` function.
        
        Args:
        mocked_doctest_runner (Mock): A mock object representing the doctest runner.
        
        Returns:
        None
        
        Summary:
        This function runs doctests for the `approx` function using the `doctest.DocTestParser` to parse the docstring and create a `doctest` object. The `approx` function is imported and used as the global namespace for the doctests. The parsed doctests
        """

        import doctest

        parser = doctest.DocTestParser()
        test = parser.get_doctest(
            approx.__doc__, {"approx": approx}, approx.__name__, None, None
        )
        mocked_doctest_runner.run(test)

    def test_unicode_plus_minus(self, testdir):
        """
        Comparing approx instances inside lists should not produce an error in the detailed diff.
        Integration test for issue #2111.
        """
        testdir.makepyfile(
            """
            import pytest
            def test_foo():
                assert [3] == [pytest.approx(4)]
        """
        )
        expected = "4.0e-06"
        result = testdir.runpytest()
        result.stdout.fnmatch_lines(
            ["*At index 0 diff: 3 != 4 ± {}".format(expected), "=* 1 failed in *="]
        )

    @pytest.mark.parametrize(
        "x",
        [
            pytest.param(None),
            pytest.param("string"),
            pytest.param(["string"], id="nested-str"),
            pytest.param([[1]], id="nested-list"),
            pytest.param({"key": "string"}, id="dict-with-string"),
            pytest.param({"key": {"key": 1}}, id="nested-dict"),
        ],
    )
    def test_expected_value_type_error(self, x):
        with pytest.raises(TypeError):
            approx(x)

    @pytest.mark.parametrize(
        "op",
        [
            pytest.param(operator.le, id="<="),
            pytest.param(operator.lt, id="<"),
            pytest.param(operator.ge, id=">="),
            pytest.param(operator.gt, id=">"),
        ],
    )
    def test_comparison_operator_type_error(self, op):
        """
        pytest.approx should raise TypeError for operators other than == and != (#2003).
        """
        with pytest.raises(TypeError):
            op(1, approx(1, rel=1e-6, abs=1e-12))

    def test_numpy_array_with_scalar(self):
        """
        Test comparing a NumPy array with a scalar using the `approx` function.
        
        This test checks the behavior of the `approx` function when comparing a NumPy array
        containing floating-point numbers close to a scalar value. The comparison is done
        using relative and absolute tolerances specified by the `rel` and `abs` parameters.
        
        Parameters:
        None
        
        Returns:
        None
        
        Functions Used:
        - numpy.array: Creates a NumPy array from a list of
        """

        np = pytest.importorskip("numpy")

        actual = np.array([1 + 1e-7, 1 - 1e-8])
        expected = 1.0

        assert actual == approx(expected, rel=5e-7, abs=0)
        assert actual != approx(expected, rel=5e-8, abs=0)
        assert approx(expected, rel=5e-7, abs=0) == actual
        assert approx(expected, rel=5e-8, abs=0) != actual

    def test_numpy_scalar_with_array(self):
        """
        Test comparing a numpy scalar with an array using the `approx` function.
        
        This test checks the behavior of the `approx` function when comparing a
        Python scalar (1.0) with a NumPy array ([1 + 1e-7, 1 - 1e-8]). The test
        uses relative and absolute tolerances to determine if the scalar is
        approximately equal to or not equal to the array.
        
        Functions Used:
        - `pytest.importors
        """

        np = pytest.importorskip("numpy")

        actual = 1.0
        expected = np.array([1 + 1e-7, 1 - 1e-8])

        assert actual == approx(expected, rel=5e-7, abs=0)
        assert actual != approx(expected, rel=5e-8, abs=0)
        assert approx(expected, rel=5e-7, abs=0) == actual
        assert approx(expected, rel=5e-8, abs=0) != actual

    def test_generic_sized_iterable_object(self):
        """
        Tests the behavior of a generic sized iterable object.
        
        This function checks if an instance of `MySizedIterable` is correctly
        recognized as having a size of 4 and its elements are equal to `[1, 2, 3, 4]`.
        
        Args:
        None (The function uses a predefined instance of `MySizedIterable`).
        
        Returns:
        None (The function asserts the equality of the expected and actual results).
        
        Important Functions:
        - `
        """

        class MySizedIterable:
            def __iter__(self):
                return iter([1, 2, 3, 4])

            def __len__(self):
                return 4

        expected = MySizedIterable()
        assert [1, 2, 3, 4] == approx(expected)
