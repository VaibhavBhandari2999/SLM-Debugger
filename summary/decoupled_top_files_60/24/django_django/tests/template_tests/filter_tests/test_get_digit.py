from django.template.defaultfilters import get_digit
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):

    def test_values(self):
        """
        Test the get_digit function.
        
        Args:
        self: The instance of the test class.
        
        This function tests the get_digit function with various inputs and checks if the output is as expected.
        
        Key Parameters:
        - num (int): The number from which to extract the digit.
        - n (int): The position of the digit to extract, starting from 1 for the least significant digit.
        
        Input/Output:
        - Input: Integer and an integer.
        - Output: Integer representing the digit
        """

        self.assertEqual(get_digit(123, 1), 3)
        self.assertEqual(get_digit(123, 2), 2)
        self.assertEqual(get_digit(123, 3), 1)
        self.assertEqual(get_digit(123, 4), 0)
        self.assertEqual(get_digit(123, 0), 123)

    def test_string(self):
        self.assertEqual(get_digit('xyz', 0), 'xyz')
