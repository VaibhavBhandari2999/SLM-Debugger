from django.forms.widgets import NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):

    @override_settings(USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        """
        Test the attributes of a NumberInput widget to ensure that non-localized attributes are correctly applied.
        
        Args:
        widget (NumberInput): The NumberInput widget instance with specified attributes.
        
        Returns:
        None: This function is used for asserting the correct HTML output and does not return any value.
        
        Key Attributes:
        - attrs (dict): A dictionary containing the attributes to be applied to the NumberInput widget, including 'max', 'min', and 'step'.
        - max (int): The maximum
        """

        widget = NumberInput(attrs={'max': 12345, 'min': 1234, 'step': 9999})
        self.check_html(
            widget, 'name', 'value',
            '<input type="number" name="name" value="value" max="12345" min="1234" step="9999">'
        )
