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
        Tests the behavior of NullBooleanField with HiddenInput widget.
        
        This function checks that the internal value of a NullBooleanField is preserved when using the HiddenInput widget. Two fields are created with initial values of True and False respectively. The HTML representation of the form is then compared to an expected string to ensure the fields are rendered correctly with the appropriate initial values.
        
        Parameters:
        - No external parameters are passed to this function.
        
        Returns:
        - None: The function asserts the expected HTML output for the form.
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
        class HiddenNullBooleanForm(Form):
            hidden_nullbool1 = NullBooleanField(widget=HiddenInput, initial=True)
            hidden_nullbool2 = NullBooleanField(widget=HiddenInput, initial=False)
        f = HiddenNullBooleanForm({'hidden_nullbool1': 'True', 'hidden_nullbool2': 'False'})
        self.assertIsNone(f.full_clean())
        self.assertTrue(f.cleaned_data['hidden_nullbool1'])
        self.assertFalse(f.cleaned_data['hidden_nullbool2'])

    def test_nullbooleanfield_4(self):
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
        
        This method checks whether the field has changed based on the provided initial and current values. The `NullBooleanField` can have three states: True, False, and None (empty). The method is used to determine if the field's state has changed between these states.
        
        Parameters:
        - initial (bool or None): The initial value of the field.
        - current (bool or None): The current value of the
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
