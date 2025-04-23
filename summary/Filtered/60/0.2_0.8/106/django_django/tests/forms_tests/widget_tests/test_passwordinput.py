from django.forms import CharField, Form, PasswordInput

from .base import WidgetTest


class PasswordInputTest(WidgetTest):
    widget = PasswordInput()

    def test_render(self):
        """
        Tests the rendering of a password input field.
        
        This function checks if the widget correctly renders a password input field. It expects the widget to generate an HTML input element with the specified type, name, and no value.
        
        Parameters:
        widget (Widget): The widget instance to be tested.
        field_type (str): The type of the input field, in this case, 'password'.
        value (str): The value to be set in the input field, which is an empty string in this case
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
