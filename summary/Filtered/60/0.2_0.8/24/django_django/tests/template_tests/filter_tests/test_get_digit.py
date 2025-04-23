from django.template.defaultfilters import get_digit
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):

    def test_values(self):
        """
        Tests the get_digit function.
        
        Args:
        self: The instance of the class.
        
        This function tests the get_digit function with the following parameters:
        - num: An integer number from which to extract a digit.
        - n: An integer representing the position of the digit to extract, starting from 1 for the least significant digit.
        
        Returns:
        None: This function is used for testing purposes and does not return any value.
        
        Raises:
        None: This function does not raise any exceptions.
        
        Examples:
        """

        self.assertEqual(get_digit(123, 1), 3)
        self.assertEqual(get_digit(123, 2), 2)
        self.assertEqual(get_digit(123, 3), 1)
        self.assertEqual(get_digit(123, 4), 0)
        self.assertEqual(get_digit(123, 0), 123)

    def test_string(self):
        self.assertEqual(get_digit('xyz', 0), 'xyz')
