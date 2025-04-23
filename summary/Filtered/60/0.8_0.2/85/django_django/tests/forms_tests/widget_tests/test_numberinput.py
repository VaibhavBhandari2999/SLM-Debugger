from django.forms.widgets import NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):

    @override_settings(USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        """
        Tests the behavior of the NumberInput widget when non-localized attributes are provided.
        
        This function creates an instance of the NumberInput widget with specified non-localized attributes and checks if the HTML output matches the expected result.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes:
        widget (NumberInput): The NumberInput widget instance with provided attributes.
        """

        widget = NumberInput(attrs={'max': 12345, 'min': 1234, 'step': 9999})
        self.check_html(
            widget, 'name', 'value',
            '<input type="number" name="name" value="value" max="12345" min="1234" step="9999">'
        )
