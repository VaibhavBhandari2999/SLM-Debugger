from django.template.defaultfilters import get_digit
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):

    def test_values(self):
        """
        Tests the get_digit function.
        
        Args:
        self: The instance of the test class.
        
        This function tests the get_digit function with various inputs and checks if the function returns the correct digit at the specified position from the right. The position is 1-indexed.
        
        Raises:
        AssertionError: If the function does not return the expected result.
        
        Test cases:
        - get_digit(123, 1) should return 3
        - get_digit(123, 2) should return
        """

        self.assertEqual(get_digit(123, 1), 3)
        self.assertEqual(get_digit(123, 2), 2)
        self.assertEqual(get_digit(123, 3), 1)
        self.assertEqual(get_digit(123, 4), 0)
        self.assertEqual(get_digit(123, 0), 123)

    def test_string(self):
        self.assertEqual(get_digit('xyz', 0), 'xyz')
