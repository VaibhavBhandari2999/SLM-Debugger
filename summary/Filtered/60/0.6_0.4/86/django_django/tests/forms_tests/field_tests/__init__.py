from django import forms


class FormFieldAssertionsMixin:

    def assertWidgetRendersTo(self, field, to):
        """
        Asserts that a given form field widget renders to the specified HTML.
        
        This function creates a simple form with a single field and checks if the HTML representation of the field matches the expected HTML.
        
        Parameters:
        field (django.forms.Field): The form field whose widget is to be rendered.
        to (str): The expected HTML representation of the field widget.
        
        Returns:
        None: The function asserts the expected result and raises an AssertionError if the HTML does not match.
        """

        class Form(forms.Form):
            f = field
        self.assertHTMLEqual(str(Form()['f']), to)
