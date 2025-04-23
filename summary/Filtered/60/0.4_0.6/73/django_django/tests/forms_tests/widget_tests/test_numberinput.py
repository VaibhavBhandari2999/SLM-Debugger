from django.forms.widgets import NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):

    @override_settings(USE_L10N=True, USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        """
        Tests the `NumberInput` widget to ensure that the specified attributes ('max', 'min', and 'step') are not localized and are correctly rendered in the HTML output. The function creates an instance of `NumberInput` with the given attributes and checks if the HTML generated matches the expected output.
        
        Parameters:
        - widget (NumberInput): The `NumberInput` widget instance with specified attributes.
        
        Returns:
        - None: The function asserts the correctness of the HTML output, so it does not return any
        """

        widget = NumberInput(attrs={'max': 12345, 'min': 1234, 'step': 9999})
        self.check_html(
            widget, 'name', 'value',
            '<input type="number" name="name" value="value" max="12345" min="1234" step="9999">'
        )
