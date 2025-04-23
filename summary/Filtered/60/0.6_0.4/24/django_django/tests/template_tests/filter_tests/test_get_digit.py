from django.template.defaultfilters import get_digit
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):

    def test_values(self):
        """
        Tests the get_digit function.
        
        Args:
        self: The instance of the test class.
        
        Methods:
        test_values: Tests the get_digit function with various inputs and expected outputs.
        
        Parameters:
        num (int): The number from which to extract the digit.
        n (int): The position of the digit to extract, starting from 1 for the least significant digit.
        
        Returns:
        int: The digit at the specified position in the number. Returns 0 if the position is greater than the
        """

        self.assertEqual(get_digit(123, 1), 3)
        self.assertEqual(get_digit(123, 2), 2)
        self.assertEqual(get_digit(123, 3), 1)
        self.assertEqual(get_digit(123, 4), 0)
        self.assertEqual(get_digit(123, 0), 123)

    def test_string(self):
        self.assertEqual(get_digit('xyz', 0), 'xyz')
