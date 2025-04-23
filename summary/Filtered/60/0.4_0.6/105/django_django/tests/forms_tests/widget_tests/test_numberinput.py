from django.forms import CharField, Form, NumberInput
from django.test import override_settings

from .base import WidgetTest


class NumberInputTests(WidgetTest):
    widget = NumberInput(attrs={"max": 12345, "min": 1234, "step": 9999})

    @override_settings(USE_THOUSAND_SEPARATOR=True)
    def test_attrs_not_localized(self):
        self.check_html(
            self.widget,
            "name",
            "value",
            '<input type="number" name="name" value="value" max="12345" min="1234" '
            'step="9999">',
        )

    def test_fieldset(self):
        """
        Tests the rendering of a form field with a custom widget that uses the `use_fieldset` attribute.
        
        This function creates a simple form with a single field using a custom widget. It then checks if the `use_fieldset` attribute of the widget is set to `False` and renders the form to ensure that the widget's HTML output does not include a fieldset tag.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Attributes:
        - `widget`: The custom widget used for the form
        """

        class TestForm(Form):
            template_name = "forms_tests/use_fieldset.html"
            field = CharField(widget=self.widget)

        form = TestForm()
        self.assertIs(self.widget.use_fieldset, False)
        self.assertHTMLEqual(
            '<div><label for="id_field">Field:</label>'
            '<input id="id_field" max="12345" min="1234" '
            'name="field" required step="9999" type="number"></div>',
            form.render(),
        )
