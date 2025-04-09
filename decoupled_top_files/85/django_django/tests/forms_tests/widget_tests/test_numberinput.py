"""
```markdown
This Python script tests the functionality of the `NumberInput` widget from Django's forms library. It includes a single test case within the `NumberInputTests` class to verify that the `attrs` parameter is not localized when creating an instance of `NumberInput`. The test ensures that custom attributes like `max`, `min`, and `step` are correctly applied to the generated HTML input element.
```

### Explanation:
- **Purpose**: The script focuses on testing the `NumberInput` widget.
- **Main Class**: `NumberInputTests` - A test class for `NumberInput`.
- **Main Function**: `test_attrs_not_localized` - A test method to check if custom attributes are correctly applied.
- **
"""
from django.forms.widgets import NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):

    @override_settings(USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        """
        Tests that the `attrs` parameter is not localized.
        
        This function creates an instance of `NumberInput` with specified attributes
        (`max`, `min`, and `step`). It then checks the HTML output of the widget
        using the `check_html` method, ensuring that the attributes are correctly
        rendered in the generated HTML input element.
        """

        widget = NumberInput(attrs={'max': 12345, 'min': 1234, 'step': 9999})
        self.check_html(
            widget, 'name', 'value',
            '<input type="number" name="name" value="value" max="12345" min="1234" step="9999">'
        )
