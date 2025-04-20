from django.template.defaultfilters import get_digit
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):
    def test_values(self):
        """
        Tests the get_digit function.
        
        Args:
        self: The instance of the class.
        
        This function tests the get_digit function with various inputs and expected outputs. The get_digit function takes two parameters: a number and a position, and returns the digit at the specified position.
        
        Key Parameters:
        - number: The number from which to extract the digit.
        - position: The position of the digit to extract, starting from 1 for the least significant digit.
        
        Expected Outputs:
        - get_digit(
        """

        self.assertEqual(get_digit(123, 1), 3)
        self.assertEqual(get_digit(123, 2), 2)
        self.assertEqual(get_digit(123, 3), 1)
        self.assertEqual(get_digit(123, 4), 0)
        self.assertEqual(get_digit(123, 0), 123)

    def test_string(self):
        self.assertEqual(get_digit("xyz", 0), "xyz")
