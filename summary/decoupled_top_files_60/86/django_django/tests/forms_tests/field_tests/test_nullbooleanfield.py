from django.forms import Form, HiddenInput, NullBooleanField, RadioSelect
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class NullBooleanFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_nullbooleanfield_clean(self):
        """
        Tests the clean method of the NullBooleanField.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key behaviors tested:
        - Returns None when the input is an empty string
        - Returns True when the input is 'True' or 'true'
        - Returns False when the input is 'False' or 'false'
        - Returns None when the input is '2' or '3' or any non-boolean string
        - Returns False when the input is '0'
        - Returns True when the input
        """

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
        Tests the behavior of NullBooleanField with HiddenInput widget.
        This function creates a form with two hidden NullBooleanFields, each initialized with a specific value. It then validates the form with inputs 'True' and 'False' for these fields. The function asserts that the cleaned data for both fields is correctly interpreted, with the first field being True and the second being False.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - hidden_nullbool1: The first NullBooleanField
        """

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
