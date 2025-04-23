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
        - Regular ASCII characters
        - Numeric characters
        - Mixed ASCII and numeric characters
        - Unicode characters (Chinese characters)
        - Unicode characters with leading and trailing spaces
        - Turkish-specific characters (ı, ç, ğ, ü, ş)
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Expected Outputs:
        - 'a' for input 'a'
        - '1' for input '1'
        -
        """

        f = SlugField(allow_unicode=True)
        self.assertEqual(f.clean('a'), 'a')
        self.assertEqual(f.clean('1'), '1')
        self.assertEqual(f.clean('a1'), 'a1')
        self.assertEqual(f.clean('你好'), '你好')
        self.assertEqual(f.clean('  你-好  '), '你-好')
        self.assertEqual(f.clean('ıçğüş'), 'ıçğüş')
        self.assertEqual(f.clean('foo-ıç-bar'), 'foo-ıç-bar')
