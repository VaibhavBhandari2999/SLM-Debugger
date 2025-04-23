from django.forms.widgets import NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):

    @override_settings(USE_L10N=True, USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        """
        Tests the `NumberInput` widget to ensure that the provided `attrs` dictionary is not localized and is directly applied to the HTML input element.
        
        Parameters:
        widget (NumberInput): The NumberInput widget instance with custom attributes.
        
        Returns:
        None: This function is used for asserting conditions and does not return any value.
        
        Key Attributes:
        - `attrs`: A dictionary containing custom attributes for the input element, such as 'max', 'min', and 'step'.
        """

        widget = NumberInput(attrs={'max': 12345, 'min': 1234, 'step': 9999})
        self.check_html(
            widget, 'name', 'value',
            '<input type="number" name="name" value="value" max="12345" min="1234" step="9999">'
        )
