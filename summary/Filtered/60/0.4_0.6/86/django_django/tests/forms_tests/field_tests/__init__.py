from django import forms


class FormFieldAssertionsMixin:

    def assertWidgetRendersTo(self, field, to):
        """
        Asserts that a given form field widget renders to the specified HTML.
        
        This function creates a simple form with the provided field and asserts that the HTML representation of the field widget matches the expected HTML string.
        
        Parameters:
        field (django.forms.Field): The form field whose widget is to be rendered.
        to (str): The expected HTML string that the field widget should render to.
        
        Returns:
        None: The function asserts the equality of the rendered HTML and the expected HTML. If they do not match
        """

        class Form(forms.Form):
            f = field
        self.assertHTMLEqual(str(Form()['f']), to)
