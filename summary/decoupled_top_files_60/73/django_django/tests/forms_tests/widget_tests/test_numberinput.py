from django.forms.widgets import NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):

    @override_settings(USE_L10N=True, USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        """
        Tests the `NumberInput` widget to ensure that the `attrs` parameter is not localized. The `NumberInput` widget is instantiated with a dictionary of HTML attributes, including 'max', 'min', and 'step'. The function checks if the widget generates the correct HTML input element with the specified attributes.
        
        Parameters:
        - widget: The `NumberInput` widget instance with specified attributes.
        
        Returns:
        - None: The function asserts the correctness of the HTML output and does not return any value.
        
        Key
        """

        widget = NumberInput(attrs={'max': 12345, 'min': 1234, 'step': 9999})
        self.check_html(
            widget, 'name', 'value',
            '<input type="number" name="name" value="value" max="12345" min="1234" step="9999">'
        )
