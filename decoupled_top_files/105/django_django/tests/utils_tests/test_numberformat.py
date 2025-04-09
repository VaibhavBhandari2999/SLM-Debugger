from decimal import Decimal
from sys import float_info

from django.test import SimpleTestCase
from django.utils.numberformat import format as nformat


class TestNumberFormat(SimpleTestCase):
    def test_format_number(self):
        """
        Format a number according to specified parameters.
        
        Args:
        value (float): The number to be formatted.
        decimal_separator (str, optional): The character to separate the integer and decimal parts. Defaults to '.'.
        decimal_places (int, optional): The number of decimal places to display. Defaults to 0.
        grouping (int, optional): The number of digits between group separators. If `force_grouping` is True, this will be enforced regardless of the value of `use
        """

        self.assertEqual(nformat(1234, "."), "1234")
        self.assertEqual(nformat(1234.2, "."), "1234.2")
        self.assertEqual(nformat(1234, ".", decimal_pos=2), "1234.00")
        self.assertEqual(nformat(1234, ".", grouping=2, thousand_sep=","), "1234")
        self.assertEqual(
            nformat(1234, ".", grouping=2, thousand_sep=",", force_grouping=True),
            "12,34",
        )
        self.assertEqual(nformat(-1234.33, ".", decimal_pos=1), "-1234.3")
        # The use_l10n parameter can force thousand grouping behavior.
        with self.settings(USE_THOUSAND_SEPARATOR=True):
            self.assertEqual(
                nformat(1234, ".", grouping=3, thousand_sep=",", use_l10n=False), "1234"
            )
            self.assertEqual(
                nformat(1234, ".", grouping=3, thousand_sep=",", use_l10n=True), "1,234"
            )

    def test_format_string(self):
        """
        Tests the `nformat` function for formatting numbers.
        
        This function tests various scenarios of the `nformat` function, which is used to format numbers based on specified parameters such as decimal position, grouping, and thousand separator. The tests cover different combinations of these parameters to ensure the function behaves as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Tests:
        - Formats a number without any special formatting.
        - Formats a number with one decimal place.
        - Adds
        """

        self.assertEqual(nformat("1234", "."), "1234")
        self.assertEqual(nformat("1234.2", "."), "1234.2")
        self.assertEqual(nformat("1234", ".", decimal_pos=2), "1234.00")
        self.assertEqual(nformat("1234", ".", grouping=2, thousand_sep=","), "1234")
        self.assertEqual(
            nformat("1234", ".", grouping=2, thousand_sep=",", force_grouping=True),
            "12,34",
        )
        self.assertEqual(nformat("-1234.33", ".", decimal_pos=1), "-1234.3")
        self.assertEqual(
            nformat(
                "10000", ".", grouping=3, thousand_sep="comma", force_grouping=True
            ),
            "10comma000",
        )

    def test_large_number(self):
        """
        Tests the nformat function with large numbers.
        
        This test function checks the behavior of the nformat function when formatting
        large numbers. It uses predefined strings `most_max` and `most_max2` to compare
        the output of the nformat function with expected results. The test cases involve
        formatting positive and negative integers, including the maximum integer value,
        its increments, and its multiples. The function `float_info.max` is used to get
        the maximum representable
        """

        most_max = (
            "{}179769313486231570814527423731704356798070567525844996"
            "598917476803157260780028538760589558632766878171540458953"
            "514382464234321326889464182768467546703537516986049910576"
            "551282076245490090389328944075868508455133942304583236903"
            "222948165808559332123348274797826204144723168738177180919"
            "29988125040402618412485836{}"
        )
        most_max2 = (
            "{}35953862697246314162905484746340871359614113505168999"
            "31978349536063145215600570775211791172655337563430809179"
            "07028764928468642653778928365536935093407075033972099821"
            "15310256415249098018077865788815173701691026788460916647"
            "38064458963316171186642466965495956524082894463374763543"
            "61838599762500808052368249716736"
        )
        int_max = int(float_info.max)
        self.assertEqual(nformat(int_max, "."), most_max.format("", "8"))
        self.assertEqual(nformat(int_max + 1, "."), most_max.format("", "9"))
        self.assertEqual(nformat(int_max * 2, "."), most_max2.format(""))
        self.assertEqual(nformat(0 - int_max, "."), most_max.format("-", "8"))
        self.assertEqual(nformat(-1 - int_max, "."), most_max.format("-", "9"))
        self.assertEqual(nformat(-2 * int_max, "."), most_max2.format("-"))

    def test_float_numbers(self):
        """
        Tests the `nformat` function for formatting floating-point numbers.
        
        This function tests the `nformat` function with various inputs, including:
        - Floating-point numbers with different magnitudes and decimal positions.
        - Handling of very small and very large numbers.
        - Formatting with and without decimal positions.
        - Thousand grouping with and without decimal positions.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any of the test cases fail.
        
        Important
        """

        tests = [
            (9e-10, 10, "0.0000000009"),
            (9e-19, 2, "0.00"),
            (0.00000000000099, 0, "0"),
            (0.00000000000099, 13, "0.0000000000009"),
            (1e16, None, "10000000000000000"),
            (1e16, 2, "10000000000000000.00"),
            # A float without a fractional part (3.) results in a ".0" when no
            # decimal_pos is given. Contrast that with the Decimal('3.') case
            # in test_decimal_numbers which doesn't return a fractional part.
            (3.0, None, "3.0"),
        ]
        for value, decimal_pos, expected_value in tests:
            with self.subTest(value=value, decimal_pos=decimal_pos):
                self.assertEqual(nformat(value, ".", decimal_pos), expected_value)
        # Thousand grouping behavior.
        self.assertEqual(
            nformat(1e16, ".", thousand_sep=",", grouping=3, force_grouping=True),
            "10,000,000,000,000,000",
        )
        self.assertEqual(
            nformat(
                1e16,
                ".",
                decimal_pos=2,
                thousand_sep=",",
                grouping=3,
                force_grouping=True,
            ),
            "10,000,000,000,000,000.00",
        )

    def test_decimal_numbers(self):
        """
        This function formats a given Decimal number according to specified parameters.
        
        Args:
        value (Decimal): The Decimal number to be formatted.
        decimal_point (str, optional): The character to use as the decimal point. Defaults to '.'.
        decimal_pos (int, optional): The number of decimal places to display. If None, no decimal places are displayed. Defaults to None.
        grouping (int, optional): The number of digits between each group separator. If None, no grouping is applied
        """

        self.assertEqual(nformat(Decimal("1234"), "."), "1234")
        self.assertEqual(nformat(Decimal("1234.2"), "."), "1234.2")
        self.assertEqual(nformat(Decimal("1234"), ".", decimal_pos=2), "1234.00")
        self.assertEqual(
            nformat(Decimal("1234"), ".", grouping=2, thousand_sep=","), "1234"
        )
        self.assertEqual(
            nformat(
                Decimal("1234"), ".", grouping=2, thousand_sep=",", force_grouping=True
            ),
            "12,34",
        )
        self.assertEqual(nformat(Decimal("-1234.33"), ".", decimal_pos=1), "-1234.3")
        self.assertEqual(
            nformat(Decimal("0.00000001"), ".", decimal_pos=8), "0.00000001"
        )
        self.assertEqual(nformat(Decimal("9e-19"), ".", decimal_pos=2), "0.00")
        self.assertEqual(nformat(Decimal(".00000000000099"), ".", decimal_pos=0), "0")
        self.assertEqual(
            nformat(
                Decimal("1e16"), ".", thousand_sep=",", grouping=3, force_grouping=True
            ),
            "10,000,000,000,000,000",
        )
        self.assertEqual(
            nformat(
                Decimal("1e16"),
                ".",
                decimal_pos=2,
                thousand_sep=",",
                grouping=3,
                force_grouping=True,
            ),
            "10,000,000,000,000,000.00",
        )
        self.assertEqual(nformat(Decimal("3."), "."), "3")
        self.assertEqual(nformat(Decimal("3.0"), "."), "3.0")
        # Very large & small numbers.
        tests = [
            ("9e9999", None, "9e+9999"),
            ("9e9999", 3, "9.000e+9999"),
            ("9e201", None, "9e+201"),
            ("9e200", None, "9e+200"),
            ("1.2345e999", 2, "1.23e+999"),
            ("9e-999", None, "9e-999"),
            ("1e-7", 8, "0.00000010"),
            ("1e-8", 8, "0.00000001"),
            ("1e-9", 8, "0.00000000"),
            ("1e-10", 8, "0.00000000"),
            ("1e-11", 8, "0.00000000"),
            ("1" + ("0" * 300), 3, "1.000e+300"),
            ("0.{}1234".format("0" * 299), 3, "0.000"),
        ]
        for value, decimal_pos, expected_value in tests:
            with self.subTest(value=value):
                self.assertEqual(
                    nformat(Decimal(value), ".", decimal_pos), expected_value
                )

    def test_decimal_subclass(self):
        """
        Wrapper for Decimal which prefixes each amount with the € symbol.
        """

        class EuroDecimal(Decimal):
            """
            Wrapper for Decimal which prefixes each amount with the € symbol.
            """

            def __format__(self, specifier, **kwargs):
                amount = super().__format__(specifier, **kwargs)
                return "€ {}".format(amount)

        price = EuroDecimal("1.23")
        self.assertEqual(nformat(price, ","), "€ 1,23")
