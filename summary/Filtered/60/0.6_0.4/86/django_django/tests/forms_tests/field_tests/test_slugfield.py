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
        - Regular ASCII characters ('a', '1', 'a1')
        - Unicode characters ('你好')
        - Whitespace and hyphen normalization ('  你-好  ')
        - Turkish characters with dotted and dotless i ('ıçğüş')
        
        The function expects a SlugField instance with `allow_unicode=True`.
        The function returns the normalized slug for each input.
        
        Parameters:
        - f (SlugField
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
        Tests the behavior of the SlugField when provided with empty or None values.
        
        This function tests the SlugField with the following configurations:
        - When `required=False`, it checks if the field returns an empty string ('') for both '' and None inputs.
        - When `required=False` and `empty_value=None`, it verifies that the field returns None for both '' and None inputs.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function tests the `clean` method of the
        """

        f = SlugField(required=False)
        self.assertEqual(f.clean(''), '')
        self.assertEqual(f.clean(None), '')
        f = SlugField(required=False, empty_value=None)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))
