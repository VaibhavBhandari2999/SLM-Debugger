from django.forms.widgets import NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):

    @override_settings(USE_L10N=True, USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        """
        Tests the attributes of a NumberInput widget to ensure that non-localized attributes are correctly applied to the HTML output.
        
        Parameters:
        widget (NumberInput): The NumberInput widget instance to test.
        
        Returns:
        None: This function is used for asserting the correctness of the widget's HTML output, hence it does not return any value.
        
        Key Attributes:
        - attrs: A dictionary containing the attributes to be applied to the widget, such as 'max', 'min', and 'step'.
        -
        """

        widget = NumberInput(attrs={'max': 12345, 'min': 1234, 'step': 9999})
        self.check_html(
            widget, 'name', 'value',
            '<input type="number" name="name" value="value" max="12345" min="1234" step="9999">'
        )
