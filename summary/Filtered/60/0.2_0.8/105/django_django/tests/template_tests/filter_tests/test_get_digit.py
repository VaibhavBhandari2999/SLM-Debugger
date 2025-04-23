from django.template.defaultfilters import get_digit
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):
    def test_values(self):
        """
        Test the get_digit function.
        
        Args:
        self: The instance of the test class.
        
        This function tests the get_digit function with various inputs to ensure it correctly extracts a specific digit from a given number based on the specified position. The position is 1-indexed, meaning the least significant digit (units place) is at position 1.
        
        Raises:
        AssertionError: If any of the test cases fail.
        
        Returns:
        None
        """

        self.assertEqual(get_digit(123, 1), 3)
        self.assertEqual(get_digit(123, 2), 2)
        self.assertEqual(get_digit(123, 3), 1)
        self.assertEqual(get_digit(123, 4), 0)
        self.assertEqual(get_digit(123, 0), 123)

    def test_string(self):
        self.assertEqual(get_digit("xyz", 0), "xyz")
