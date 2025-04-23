from django.forms import Form, HiddenInput, NullBooleanField, RadioSelect
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class NullBooleanFieldTest(FormFieldAssertionsMixin, SimpleTestCase):
    def test_nullbooleanfield_clean(self):
        """
        Tests the clean method of the NullBooleanField.
        
        This method tests the clean method of the NullBooleanField to ensure it handles various input values correctly. The clean method should return None for empty strings, True for 'true' or '1', False for 'false' or '0', and raise a ValidationError for any other input.
        
        Parameters:
        - No explicit parameters are passed in the function.
        
        Returns:
        - None: The function does not return anything, but rather asserts the expected behavior of the clean
        """

        f = NullBooleanField()
        self.assertIsNone(f.clean(""))
        self.assertTrue(f.clean(True))
        self.assertFalse(f.clean(False))
        self.assertIsNone(f.clean(None))
        self.assertFalse(f.clean("0"))
        self.assertTrue(f.clean("1"))
        self.assertIsNone(f.clean("2"))
        self.assertIsNone(f.clean("3"))
        self.assertIsNone(f.clean("hello"))
        self.assertTrue(f.clean("true"))
        self.assertFalse(f.clean("false"))

    def test_nullbooleanfield_2(self):
        # The internal value is preserved if using HiddenInput (#7753).
        class HiddenNullBooleanForm(Form):
            hidden_nullbool1 = NullBooleanField(widget=HiddenInput, initial=True)
            hidden_nullbool2 = NullBooleanField(widget=HiddenInput, initial=False)

        f = HiddenNullBooleanForm()
        self.assertHTMLEqual(
            str(f),
            '<input type="hidden" name="hidden_nullbool1" value="True" '
            'id="id_hidden_nullbool1">'
            '<input type="hidden" name="hidden_nullbool2" value="False" '
            'id="id_hidden_nullbool2">',
        )

    def test_nullbooleanfield_3(self):
        class HiddenNullBooleanForm(Form):
            hidden_nullbool1 = NullBooleanField(widget=HiddenInput, initial=True)
            hidden_nullbool2 = NullBooleanField(widget=HiddenInput, initial=False)

        f = HiddenNullBooleanForm(
            {"hidden_nullbool1": "True", "hidden_nullbool2": "False"}
        )
        self.assertIsNone(f.full_clean())
        self.assertTrue(f.cleaned_data["hidden_nullbool1"])
        self.assertFalse(f.cleaned_data["hidden_nullbool2"])

    def test_nullbooleanfield_4(self):
        """
        Tests the behavior of the NullBooleanField with different input values.
        
        This function tests the NullBooleanField with three instances, each configured with the same choices for a radio select widget. The test checks the behavior of the field when different values are provided in the form data. Specifically, it verifies that:
        - The field correctly interprets '1' as True.
        - The field correctly interprets '0' as False.
        - The field correctly handles an empty string as None.
        
        Parameters:
        - null
        """

        # Make sure we're compatible with MySQL, which uses 0 and 1 for its
        # boolean values (#9609).
        NULLBOOL_CHOICES = (("1", "Yes"), ("0", "No"), ("", "Unknown"))

        class MySQLNullBooleanForm(Form):
            nullbool0 = NullBooleanField(widget=RadioSelect(choices=NULLBOOL_CHOICES))
            nullbool1 = NullBooleanField(widget=RadioSelect(choices=NULLBOOL_CHOICES))
            nullbool2 = NullBooleanField(widget=RadioSelect(choices=NULLBOOL_CHOICES))

        f = MySQLNullBooleanForm({"nullbool0": "1", "nullbool1": "0", "nullbool2": ""})
        self.assertIsNone(f.full_clean())
        self.assertTrue(f.cleaned_data["nullbool0"])
        self.assertFalse(f.cleaned_data["nullbool1"])
        self.assertIsNone(f.cleaned_data["nullbool2"])

    def test_nullbooleanfield_changed(self):
        """
        Tests the behavior of the `has_changed` method for a NullBooleanField.
        
        This method checks whether the field has changed from its initial value. The NullBooleanField can have three states: True, False, and None (unknown). The `has_changed` method is used to determine if the field's state has changed from its initial value.
        
        Parameters:
        - f: The NullBooleanField instance to test.
        
        Returns:
        None: This function does not return a value, it only asserts the
        """

        f = NullBooleanField()
        self.assertTrue(f.has_changed(False, None))
        self.assertTrue(f.has_changed(None, False))
        self.assertFalse(f.has_changed(None, None))
        self.assertFalse(f.has_changed(False, False))
        self.assertTrue(f.has_changed(True, False))
        self.assertTrue(f.has_changed(True, None))
        self.assertTrue(f.has_changed(True, False))
        # HiddenInput widget sends string values for boolean but doesn't clean
        # them in value_from_datadict.
        self.assertFalse(f.has_changed(False, "False"))
        self.assertFalse(f.has_changed(True, "True"))
        self.assertFalse(f.has_changed(None, ""))
        self.assertTrue(f.has_changed(False, "True"))
        self.assertTrue(f.has_changed(True, "False"))
        self.assertTrue(f.has_changed(None, "False"))
