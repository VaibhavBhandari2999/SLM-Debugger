from django import forms


class FormFieldAssertionsMixin:

    def assertWidgetRendersTo(self, field, to):
        """
        Asserts that a form field widget renders to the expected HTML.
        
        This function is used to verify that a form field's widget produces the expected HTML output when rendered.
        
        Parameters:
        field (Field): The form field whose widget is to be rendered.
        to (str): The expected HTML output of the widget.
        
        Returns:
        None: This function does not return any value. It raises an assertion error if the rendered HTML does not match the expected output.
        """

        class Form(forms.Form):
            f = field
        self.assertHTMLEqual(str(Form()['f']), to)
