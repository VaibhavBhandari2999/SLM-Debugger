from django.forms import CharField, Form, PasswordInput

from .base import WidgetTest


class PasswordInputTest(WidgetTest):
    widget = PasswordInput()

    def test_render(self):
        """
        Tests the rendering of a password input field.
        
        Args:
        self: The instance of the test class.
        
        This function checks the HTML output of the widget when rendering a password input field. It expects an empty string as input and verifies that the rendered HTML matches the expected output, which is an input element of type "password" with the specified name attribute.
        """

        self.check_html(
            self.widget, "password", "", html='<input type="password" name="password">'
        )

    def test_render_ignore_value(self):
        self.check_html(
            self.widget,
            "password",
            "secret",
            html='<input type="password" name="password">',
        )

    def test_render_value_true(self):
        """
        The render_value argument lets you specify whether the widget should
        render its value. For security reasons, this is off by default.
        """
        widget = PasswordInput(render_value=True)
        self.check_html(
            widget, "password", "", html='<input type="password" name="password">'
        )
        self.check_html(
            widget, "password", None, html='<input type="password" name="password">'
        )
        self.check_html(
            widget,
            "password",
            "test@example.com",
            html='<input type="password" name="password" value="test@example.com">',
        )

    def test_fieldset(self):
        """
        Tests the rendering of a form field with a custom widget that uses a fieldset.
        
        This function checks the rendering of a form field using a custom widget. The widget's `use_fieldset` attribute is set to `False` by default. The function creates a form with a single character field using the specified widget. It then renders the form and asserts that the rendered HTML does not include a fieldset, as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        -
        """

        class TestForm(Form):
            template_name = "forms_tests/use_fieldset.html"
            field = CharField(widget=self.widget)

        form = TestForm()
        self.assertIs(self.widget.use_fieldset, False)
        self.assertHTMLEqual(
            '<div><label for="id_field">Field:</label>'
            '<input type="password" name="field" required id="id_field"></div>',
            form.render(),
        )
