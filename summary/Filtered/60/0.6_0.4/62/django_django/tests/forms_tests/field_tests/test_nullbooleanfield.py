from django.forms import Form, HiddenInput, NullBooleanField, RadioSelect
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class NullBooleanFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_nullbooleanfield_clean(self):
        f = NullBooleanField()
        self.assertIsNone(f.clean(''))
        self.assertTrue(f.clean(True))
        self.assertFalse(f.clean(False))
        self.assertIsNone(f.clean(None))
        self.assertFalse(f.clean('0'))
        self.assertTrue(f.clean('1'))
        self.assertIsNone(f.clean('2'))
        self.assertIsNone(f.clean('3'))
        self.assertIsNone(f.clean('hello'))
        self.assertTrue(f.clean('true'))
        self.assertFalse(f.clean('false'))

    def test_nullbooleanfield_2(self):
        """
        Tests the behavior of the NullBooleanField with HiddenInput widget.
        
        This function verifies that the internal value of a NullBooleanField is preserved when using the HiddenInput widget. It creates a form with two fields, each initialized with a specific value (True and False) and uses HiddenInput as the widget. The function then asserts that the HTML output correctly reflects these initial values.
        
        Parameters:
        - No external parameters are needed for this function.
        
        Returns:
        - None. The function asserts the expected HTML output.
        """

        # The internal value is preserved if using HiddenInput (#7753).
        class HiddenNullBooleanForm(Form):
            hidden_nullbool1 = NullBooleanField(widget=HiddenInput, initial=True)
            hidden_nullbool2 = NullBooleanField(widget=HiddenInput, initial=False)
        f = HiddenNullBooleanForm()
        self.assertHTMLEqual(
            '<input type="hidden" name="hidden_nullbool1" value="True" id="id_hidden_nullbool1">'
            '<input type="hidden" name="hidden_nullbool2" value="False" id="id_hidden_nullbool2">',
            str(f)
        )

    def test_nullbooleanfield_3(self):
        """
        Test the behavior of NullBooleanField with HiddenInput widget.
        
        This function tests the NullBooleanField widget when it is hidden in a form.
        It creates a form with two fields, 'hidden_nullbool1' and 'hidden_nullbool2', both using the HiddenInput widget.
        The initial values for these fields are set to True and False, respectively.
        The function then submits values 'True' and 'False' for these fields and checks if the form can be cleaned without errors.
        It also verifies
        """

        class HiddenNullBooleanForm(Form):
            hidden_nullbool1 = NullBooleanField(widget=HiddenInput, initial=True)
            hidden_nullbool2 = NullBooleanField(widget=HiddenInput, initial=False)
        f = HiddenNullBooleanForm({'hidden_nullbool1': 'True', 'hidden_nullbool2': 'False'})
        self.assertIsNone(f.full_clean())
        self.assertTrue(f.cleaned_data['hidden_nullbool1'])
        self.assertFalse(f.cleaned_data['hidden_nullbool2'])

    def test_nullbooleanfield_4(self):
        """
        Tests for the NullBooleanField.
        
        This function tests the behavior of the NullBooleanField with different inputs and ensures that it correctly handles null values. The form is instantiated with three fields, each configured with the same choices for a null boolean field. The function then validates the form with specific input values and checks if the cleaned data matches the expected results.
        
        Parameters:
        - self: The instance of the test case class.
        
        Key Parameters:
        - NULLBOOL_CHOICES: A tuple of tuples representing the choices
        """

        # Make sure we're compatible with MySQL, which uses 0 and 1 for its
        # boolean values (#9609).
        NULLBOOL_CHOICES = (('1', 'Yes'), ('0', 'No'), ('', 'Unknown'))

        class MySQLNullBooleanForm(Form):
            nullbool0 = NullBooleanField(widget=RadioSelect(choices=NULLBOOL_CHOICES))
            nullbool1 = NullBooleanField(widget=RadioSelect(choices=NULLBOOL_CHOICES))
            nullbool2 = NullBooleanField(widget=RadioSelect(choices=NULLBOOL_CHOICES))
        f = MySQLNullBooleanForm({'nullbool0': '1', 'nullbool1': '0', 'nullbool2': ''})
        self.assertIsNone(f.full_clean())
        self.assertTrue(f.cleaned_data['nullbool0'])
        self.assertFalse(f.cleaned_data['nullbool1'])
        self.assertIsNone(f.cleaned_data['nullbool2'])

    def test_nullbooleanfield_changed(self):
        """
        Tests the behavior of the `NullBooleanField` class's `has_changed` method.
        
        This method checks if the field has changed based on the provided initial and current values. The `NullBooleanField` can take three states: True, False, and None (empty). The `has_changed` method returns True if the field's state has changed from the initial value.
        
        Parameters:
        - initial (bool or None): The initial value of the field.
        - current (bool or None):
        """

        f = NullBooleanField()
        self.assertTrue(f.has_changed(False, None))
        self.assertTrue(f.has_changed(None, False))
        self.assertFalse(f.has_changed(None, None))
        self.assertFalse(f.has_changed(False, False))
        self.assertTrue(f.has_changed(True, False))
        self.assertTrue(f.has_changed(True, None))
        self.assertTrue(f.has_changed(True, False))
        # HiddenInput widget sends string values for boolean but doesn't clean them in value_from_datadict
        self.assertFalse(f.has_changed(False, 'False'))
        self.assertFalse(f.has_changed(True, 'True'))
        self.assertFalse(f.has_changed(None, ''))
        self.assertTrue(f.has_changed(False, 'True'))
        self.assertTrue(f.has_changed(True, 'False'))
        self.assertTrue(f.has_changed(None, 'False'))
