"""
```markdown
This Python script contains unit tests for Django's SlugField. It includes tests for normalization, handling of Unicode characters, and behavior with empty values. The `SlugFieldTest` class defines several methods to validate the expected behavior of the SlugField under different conditions.
```

### Docstring:
```python
"""
from django.forms import SlugField
from django.test import SimpleTestCase


class SlugFieldTest(SimpleTestCase):

    def test_slugfield_normalization(self):
        f = SlugField()
        self.assertEqual(f.clean('    aa-bb-cc    '), 'aa-bb-cc')

    def test_slugfield_unicode_normalization(self):
        """
        Tests the behavior of the SlugField when allowing Unicode characters. The function creates a SlugField instance with allow_unicode set to True, and tests its clean method with various inputs, including plain ASCII characters, digits, mixed ASCII and Unicode characters, and special Unicode characters. It ensures that the field correctly normalizes and sanitizes the input strings according to the specified rules.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Used:
        - SlugField: Creates a SlugField instance with
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
        Tests the behavior of the SlugField when cleaning empty values or None.
        
        This function tests the `clean` method of the `SlugField` class with different configurations:
        - When `required` is set to `False`, an empty string or `None` is cleaned to an empty string.
        - When `empty_value` is set to `None` and `required` is `False`, an empty string or `None` is cleaned to `None`.
        
        Args:
        None
        """

        f = SlugField(required=False)
        self.assertEqual(f.clean(''), '')
        self.assertEqual(f.clean(None), '')
        f = SlugField(required=False, empty_value=None)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))
