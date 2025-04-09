# RemovedInDjango50
from django.forms import CharField, EmailField, Form, HiddenInput
from django.forms.utils import ErrorList
from django.test import SimpleTestCase, ignore_warnings
from django.utils.deprecation import RemovedInDjango50Warning

from .test_forms import Person


class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        """
        Generate an HTML representation of the error list as a series of <div> elements.
        
        Args:
        None (The method operates on the instance's attributes).
        
        Returns:
        str: An HTML string representing the error list, where each error is enclosed in a <div> element with the class "error".
        
        Summary:
        This function takes an error list (self) and returns an HTML string. It uses a generator expression to iterate over each error in the list, creating a <div
        """

        if not self:
            return ""
        return '<div class="errorlist">%s</div>' % "".join(
            f'<div class="error">{error}</div>' for error in self
        )


class DeprecationTests(SimpleTestCase):
    def test_deprecation_warning_html_output(self):
        """
        Tests the deprecation warning for the _html_output method of django.forms.BaseForm. Raises a RemovedInDjango50Warning if the method is called with specific arguments. The method checks for the deprecation of _html_output and suggests using render() and get_context() instead. The test uses a Person form instance to validate the warning message.
        """

        msg = (
            "django.forms.BaseForm._html_output() is deprecated. Please use "
            ".render() and .get_context() instead."
        )
        with self.assertRaisesMessage(RemovedInDjango50Warning, msg):
            form = Person()
            form._html_output(
                normal_row='<p id="p_%(field_name)s"></p>',
                error_row="%s",
                row_ender="</p>",
                help_text_html=" %s",
                errors_on_separate_row=True,
            )

    def test_deprecation_warning_error_list(self):
        """
        Tests the deprecation warning for DivErrorList.
        
        This function checks if a deprecation warning is raised when using
        DivErrorList with a form. It creates an instance of the EmailForm with
        specified data and an error class set to DivErrorList. The function then
        asserts that a RemovedInDjango50Warning is raised with a specific message
        when calling `as_p()` on the form instance.
        
        Args:
        self: The test case instance.
        """

        class EmailForm(Form):
            email = EmailField()
            comment = CharField()

        data = {"email": "invalid"}
        f = EmailForm(data, error_class=DivErrorList)
        msg = (
            "Returning a plain string from DivErrorList is deprecated. Please "
            "customize via the template system instead."
        )
        with self.assertRaisesMessage(RemovedInDjango50Warning, msg):
            f.as_p()


@ignore_warnings(category=RemovedInDjango50Warning)
class DeprecatedTests(SimpleTestCase):
    def test_errorlist_override_str(self):
        """
        Tests the override of the `__str__` method in DivErrorList for a form with specific fields and validation errors.
        
        Args:
        self: The instance of the test case.
        
        Important Functions:
        - `CharField`: A character field with specified max length and required status.
        - `EmailField`: An email field with validation for email format.
        - `DivErrorList`: An error list class that overrides the `__str__` method to display errors in div tags
        """

        class CommentForm(Form):
            name = CharField(max_length=50, required=False)
            email = EmailField()
            comment = CharField()

        data = {"email": "invalid"}
        f = CommentForm(data, auto_id=False, error_class=DivErrorList)
        self.assertHTMLEqual(
            f.as_p(),
            '<p>Name: <input type="text" name="name" maxlength="50"></p>'
            '<div class="errorlist">'
            '<div class="error">Enter a valid email address.</div></div>'
            '<p>Email: <input type="email" name="email" value="invalid" required></p>'
            '<div class="errorlist">'
            '<div class="error">This field is required.</div></div>'
            '<p>Comment: <input type="text" name="comment" required></p>',
        )

    def test_field_name(self):
        """#5749 - `field_name` may be used as a key in _html_output()."""

        class SomeForm(Form):
            some_field = CharField()

            def as_p(self):
                """
                Generates an HTML paragraph element for form fields. This method outputs a paragraph tag with an ID based on the field name. It uses the `_html_output` method to format the output, taking into account normal rows, error rows, row endings, help text, and error placement. The `normal_row` parameter specifies the HTML structure for a regular field, `error_row` defines how errors are displayed, `row_ender` indicates the end of each row, `help_text_html` integrates
                """

                return self._html_output(
                    normal_row='<p id="p_%(field_name)s"></p>',
                    error_row="%s",
                    row_ender="</p>",
                    help_text_html=" %s",
                    errors_on_separate_row=True,
                )

        form = SomeForm()
        self.assertHTMLEqual(form.as_p(), '<p id="p_some_field"></p>')

    def test_field_without_css_classes(self):
        """
        `css_classes` may be used as a key in _html_output() (empty classes).
        """

        class SomeForm(Form):
            some_field = CharField()

            def as_p(self):
                return self._html_output(
                    normal_row='<p class="%(css_classes)s"></p>',
                    error_row="%s",
                    row_ender="</p>",
                    help_text_html=" %s",
                    errors_on_separate_row=True,
                )

        form = SomeForm()
        self.assertHTMLEqual(form.as_p(), '<p class=""></p>')

    def test_field_with_css_class(self):
        """
        `css_classes` may be used as a key in _html_output() (class comes
        from required_css_class in this case).
        """

        class SomeForm(Form):
            some_field = CharField()
            required_css_class = "foo"

            def as_p(self):
                return self._html_output(
                    normal_row='<p class="%(css_classes)s"></p>',
                    error_row="%s",
                    row_ender="</p>",
                    help_text_html=" %s",
                    errors_on_separate_row=True,
                )

        form = SomeForm()
        self.assertHTMLEqual(form.as_p(), '<p class="foo"></p>')

    def test_field_name_with_hidden_input(self):
        """
        BaseForm._html_output() should merge all the hidden input fields and
        put them in the last row.
        """

        class SomeForm(Form):
            hidden1 = CharField(widget=HiddenInput)
            custom = CharField()
            hidden2 = CharField(widget=HiddenInput)

            def as_p(self):
                return self._html_output(
                    normal_row="<p%(html_class_attr)s>%(field)s %(field_name)s</p>",
                    error_row="%s",
                    row_ender="</p>",
                    help_text_html=" %s",
                    errors_on_separate_row=True,
                )

        form = SomeForm()
        self.assertHTMLEqual(
            form.as_p(),
            '<p><input id="id_custom" name="custom" type="text" required> custom'
            '<input id="id_hidden1" name="hidden1" type="hidden">'
            '<input id="id_hidden2" name="hidden2" type="hidden"></p>',
        )

    def test_field_name_with_hidden_input_and_non_matching_row_ender(self):
        """
        BaseForm._html_output() should merge all the hidden input fields and
        put them in the last row ended with the specific row ender.
        """

        class SomeForm(Form):
            hidden1 = CharField(widget=HiddenInput)
            custom = CharField()
            hidden2 = CharField(widget=HiddenInput)

            def as_p(self):
                return self._html_output(
                    normal_row="<p%(html_class_attr)s>%(field)s %(field_name)s</p>",
                    error_row="%s",
                    row_ender="<hr><hr>",
                    help_text_html=" %s",
                    errors_on_separate_row=True,
                )

        form = SomeForm()
        self.assertHTMLEqual(
            form.as_p(),
            '<p><input id="id_custom" name="custom" type="text" required> custom</p>\n'
            '<input id="id_hidden1" name="hidden1" type="hidden">'
            '<input id="id_hidden2" name="hidden2" type="hidden"><hr><hr>',
        )
