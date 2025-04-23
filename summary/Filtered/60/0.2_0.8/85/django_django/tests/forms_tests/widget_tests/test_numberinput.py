from django.forms.widgets import NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):

    @override_settings(USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        """
        Tests the `attrs` parameter of the NumberInput widget to ensure that non-localized attributes are correctly applied to the generated HTML input element. The function creates a NumberInput widget with specified max, min, and step attributes and checks if the HTML output matches the expected format.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - `attrs`: A dictionary containing non-localized attributes to be applied to the input element, such as 'max', 'min', and 'step'.
        """

        widget = NumberInput(attrs={'max': 12345, 'min': 1234, 'step': 9999})
        self.check_html(
            widget, 'name', 'value',
            '<input type="number" name="name" value="value" max="12345" min="1234" step="9999">'
        )
