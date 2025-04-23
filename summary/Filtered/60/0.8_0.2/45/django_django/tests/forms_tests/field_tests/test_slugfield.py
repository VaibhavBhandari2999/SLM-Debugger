from django.forms import SlugField
from django.test import SimpleTestCase


class SlugFieldTest(SimpleTestCase):

    def test_slugfield_normalization(self):
        f = SlugField()
        self.assertEqual(f.clean('    aa-bb-cc    '), 'aa-bb-cc')

    def test_slugfield_unicode_normalization(self):
        """
        Test the SlugField with Unicode normalization.
        
        This function tests the SlugField with the `allow_unicode=True` parameter to ensure it correctly handles various types of input, including ASCII characters, digits, and Unicode characters. The function normalizes the input to a standard form and checks if the cleaned output matches the expected result.
        
        Parameters:
        None
        
        Returns:
        None
        
        Test Cases:
        - 'a' is cleaned to 'a'.
        - '1' is cleaned to '1'.
        - 'a1
        """

        f = SlugField(allow_unicode=True)
        self.assertEqual(f.clean('a'), 'a')
        self.assertEqual(f.clean('1'), '1')
        self.assertEqual(f.clean('a1'), 'a1')
        self.assertEqual(f.clean('你好'), '你好')
        self.assertEqual(f.clean('  你-好  '), '你-好')
        self.assertEqual(f.clean('ıçğüş'), 'ıçğüş')
        self.assertEqual(f.clean('foo-ıç-bar'), 'foo-ıç-bar')
