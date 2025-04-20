from django.forms import SlugField
from django.test import SimpleTestCase


class SlugFieldTest(SimpleTestCase):

    def test_slugfield_normalization(self):
        f = SlugField()
        self.assertEqual(f.clean('    aa-bb-cc    '), 'aa-bb-cc')

    def test_slugfield_unicode_normalization(self):
        """
        Test the SlugField with Unicode normalization.
        
        This function tests the SlugField with various inputs, including:
        - Regular characters (e.g., 'a', '1', 'a1')
        - Unicode characters (e.g., '你好')
        - Whitespace and special characters (e.g., '  你-好  ')
        - Turkish-specific characters (e.g., 'ıçğüş')
        
        Parameters:
        - None
        
        Returns:
        - None
        
        The function asserts that the SlugField correctly handles and normal
        """

        f = SlugField(allow_unicode=True)
        self.assertEqual(f.clean('a'), 'a')
        self.assertEqual(f.clean('1'), '1')
        self.assertEqual(f.clean('a1'), 'a1')
        self.assertEqual(f.clean('你好'), '你好')
        self.assertEqual(f.clean('  你-好  '), '你-好')
        self.assertEqual(f.clean('ıçğüş'), 'ıçğüş')
        self.assertEqual(f.clean('foo-ıç-bar'), 'foo-ıç-bar')

    def test_empty_value(self):
        """
        Tests the behavior of the SlugField when dealing with empty values and different configurations.
        
        Parameters:
        - f: A SlugField instance with specified configurations.
        
        Returns:
        - None: The function does not return anything, but it asserts the expected behavior of the SlugField.
        
        Key Parameters:
        - required (bool): Determines if the field is required. Default is False.
        - empty_value: The value to return when the input is empty. Default is '' (empty string).
        
        Key Behavior:
        - When `required=False
        """

        f = SlugField(required=False)
        self.assertEqual(f.clean(''), '')
        self.assertEqual(f.clean(None), '')
        f = SlugField(required=False, empty_value=None)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))
