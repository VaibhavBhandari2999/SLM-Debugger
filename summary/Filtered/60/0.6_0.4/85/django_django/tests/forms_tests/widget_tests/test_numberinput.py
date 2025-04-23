from django.forms.widgets import NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):

    @override_settings(USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        """
        Tests the `NumberInput` widget to ensure that the `attrs` parameter is correctly applied to the HTML output. The `attrs` parameter is expected to be a dictionary containing HTML attributes such as 'max', 'min', and 'step'. The function creates an instance of `NumberInput` with specified `attrs` and checks if the generated HTML matches the expected output.
        
        Parameters:
        - widget: An instance of the `NumberInput` widget with specified `attrs`.
        
        Returns:
        - None: The
        """

        widget = NumberInput(attrs={'max': 12345, 'min': 1234, 'step': 9999})
        self.check_html(
            widget, 'name', 'value',
            '<input type="number" name="name" value="value" max="12345" min="1234" step="9999">'
        )
