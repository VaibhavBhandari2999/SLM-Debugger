from django import forms


class FormFieldAssertionsMixin:

    def assertWidgetRendersTo(self, field, to):
        """
        Asserts that a given form field widget renders to the specified HTML.
        
        This function is used to verify that a form field's widget produces the expected HTML output.
        
        Parameters:
        field (django.forms.Field): The form field whose widget is to be rendered.
        to (str): The expected HTML output of the widget.
        
        Returns:
        None: The function asserts the expected HTML output and raises an AssertionError if the output does not match the expected value.
        
        Example Usage:
        >>> assertWidgetRendersTo
        """

        class Form(forms.Form):
            f = field
        self.assertHTMLEqual(str(Form()['f']), to)
