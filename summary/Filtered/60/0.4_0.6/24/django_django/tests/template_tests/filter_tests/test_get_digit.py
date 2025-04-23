from django.template.defaultfilters import get_digit
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):

    def test_values(self):
        """
        Test the get_digit function.
        
        Args:
        self: The instance of the class running the test.
        
        This method tests the get_digit function with various inputs and expected outputs:
        - get_digit(123, 1) should return 3
        - get_digit(123, 2) should return 2
        - get_digit(123, 3) should return 1
        - get_digit(123, 4) should return 0
        - get
        """

        self.assertEqual(get_digit(123, 1), 3)
        self.assertEqual(get_digit(123, 2), 2)
        self.assertEqual(get_digit(123, 3), 1)
        self.assertEqual(get_digit(123, 4), 0)
        self.assertEqual(get_digit(123, 0), 123)

    def test_string(self):
        self.assertEqual(get_digit('xyz', 0), 'xyz')
