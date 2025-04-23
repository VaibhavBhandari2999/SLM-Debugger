from django.forms import SlugField
from django.test import SimpleTestCase


class SlugFieldTest(SimpleTestCase):

    def test_slugfield_normalization(self):
        f = SlugField()
        self.assertEqual(f.clean('    aa-bb-cc    '), 'aa-bb-cc')

    def test_slugfield_unicode_normalization(self):
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
        Tests the behavior of the SlugField when dealing with empty values.
        
        This function tests the SlugField with different configurations to ensure it handles empty values and None correctly.
        
        Parameters:
        None (The function uses predefined instances of SlugField for testing).
        
        Returns:
        None (The function asserts expected outcomes through internal checks).
        
        Key Points:
        - The first SlugField instance is configured with `required=False`, and it should return an empty string for both '' and None.
        - The second SlugField instance is configured with
        """

        f = SlugField(required=False)
        self.assertEqual(f.clean(''), '')
        self.assertEqual(f.clean(None), '')
        f = SlugField(required=False, empty_value=None)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))
