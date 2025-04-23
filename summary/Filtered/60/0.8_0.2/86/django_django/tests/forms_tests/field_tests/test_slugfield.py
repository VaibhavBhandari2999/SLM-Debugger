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
        Tests the behavior of the SlugField when provided with empty or None values.
        
        Parameters:
        f (SlugField): The SlugField instance to test.
        
        Returns:
        None: The function asserts the expected outcomes and does not return any value.
        
        Key Parameters:
        - `required`: A boolean indicating whether the field is required. If False, the field can accept empty or None values.
        - `empty_value`: The value to use when the field is empty. If not provided, the default is
        """

        f = SlugField(required=False)
        self.assertEqual(f.clean(''), '')
        self.assertEqual(f.clean(None), '')
        f = SlugField(required=False, empty_value=None)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))
