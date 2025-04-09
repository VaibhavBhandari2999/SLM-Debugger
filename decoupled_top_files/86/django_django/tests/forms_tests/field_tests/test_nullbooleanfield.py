"""
The provided Python file contains unit tests for the `NullBooleanField` class from Django's forms module. The file defines a test class `NullBooleanFieldTest` that inherits from `SimpleTestCase` and `FormFieldAssertionsMixin`. The class includes several test methods to validate the behavior of the `NullBooleanField` under different conditions:

1. **test_nullbooleanfield_clean**: Verifies the `clean` method of `NullBooleanField` by testing its response to various input values, including empty strings, boolean values, numeric strings, and non-boolean strings.
2. **test_nullbooleanfield_2**: Ensures that the internal value of a `NullBooleanField` is correctly preserved when using the `HiddenInput` widget.
3
"""
from django.forms import Form, HiddenInput, NullBooleanField, RadioSelect
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class NullBooleanFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_nullbooleanfield_clean(self):
        """
        Tests the clean method of the NullBooleanField class.
        
        This method verifies that the clean method correctly handles various inputs, including empty strings, boolean values (True and False), None, numeric strings ('0' and '1'), non-boolean strings ('2', '3', and 'hello'), and boolean-like strings ('true' and 'false'). The method returns None for empty strings, True for 'true' and '1', False for 'false' and '0', and raises an
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
        """
        Test the behavior of NullBooleanField with HiddenInput widget.
        
        This function verifies that the internal value of a NullBooleanField is
        correctly preserved when using the HiddenInput widget. It creates a form
        with two fields, `hidden_nullbool1` and `hidden_nullbool2`, both using
        the HiddenInput widget and initialized with specific values. The function
        then asserts that the generated HTML matches the expected output.
        
        - **Important Functions**: `NullBooleanField`,
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
        Tests the behavior of NullBooleanField with HiddenInput widget when form data is submitted.
        
        This function creates a form with two NullBooleanFields initialized to True and False respectively. It then processes the form submission where one field is set to 'True' and the other to 'False'. The function asserts that the cleaned data correctly interprets these values as None, True, and False after validation.
        
        Important Functions:
        - NullBooleanField
        - HiddenInput
        - HiddenNull
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
        Tests the behavior of the NullBooleanField with different inputs.
        
        This function creates a form with three instances of NullBooleanField,
        each configured with the same choices. It then validates the form with
        specific input values: '1' for true, '0' for false, and an empty string
        for unknown. The function asserts that the cleaned data correctly
        interprets these inputs as True, False, and None respectively.
        
        - `NullBooleanField`: The field type
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
        Tests the behavior of the `NullBooleanField` when checking if its value has changed. This function evaluates the `has_changed` method of the `NullBooleanField` class with various input combinations, including `False`, `None`, and string representations of boolean values. The function uses assertions to verify the expected outcomes for each case.
        
        Important Functions:
        - `has_changed`: Determines if the field's value has changed based on the provided old and new values.
        - `NullBooleanField
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
