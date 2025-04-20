from django.forms import Form, HiddenInput, NullBooleanField, RadioSelect
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class NullBooleanFieldTest(FormFieldAssertionsMixin, SimpleTestCase):
    def test_nullbooleanfield_clean(self):
        """
        Tests the clean method of the NullBooleanField class.
        
        This function tests the clean method of the NullBooleanField class, which is responsible for validating and converting input values to the appropriate boolean or None type. The function checks the following scenarios:
        - Cleaning an empty string ("") should return None.
        - Cleaning the value "True" should return True.
        - Cleaning the value "False" should return False.
        - Cleaning a None value should return None.
        - Cleaning the string "0" should return False
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
        """
        Tests the behavior of the NullBooleanField with HiddenInput widget.
        
        This function verifies that the internal value of a NullBooleanField is preserved when using the HiddenInput widget. It creates a form with two fields, each configured with the HiddenInput widget and an initial value. The function then renders the form and asserts that the HTML output matches the expected values for the initial states of the fields.
        
        Parameters:
        - No external parameters are required for this function.
        
        Returns:
        - None. The function asserts the expected
        """

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
        """
        Tests the behavior of the NullBooleanField with HiddenInput widget.
        
        This function creates a form with two hidden NullBooleanFields, each initialized with a specific value. It then validates the form with certain input data and checks if the cleaned data matches the expected results.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - No explicit parameters are passed to the function.
        
        Key Keywords:
        - No keyword arguments are used in the function call.
        
        Input:
        - The form is validated with
        """

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
        
        This method checks if the field has changed between two states. The key parameters are:
        - `False`: Represents a boolean value of False.
        - `None`: Represents a null or unknown value.
        
        The method returns a boolean indicating whether the field has changed.
        
        Key behaviors tested:
        - Changes from `False` to `None`.
        - Changes from `None` to `False`.
        - No change when both are `None`.
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
