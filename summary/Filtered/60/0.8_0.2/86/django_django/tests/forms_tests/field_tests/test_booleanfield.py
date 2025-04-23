import pickle

from django.core.exceptions import ValidationError
from django.forms import BooleanField
from django.test import SimpleTestCase


class BooleanFieldTest(SimpleTestCase):

    def test_booleanfield_clean_1(self):
        f = BooleanField()
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertTrue(f.clean(True))
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(False)
        self.assertTrue(f.clean(1))
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(0)
        self.assertTrue(f.clean('Django rocks'))
        self.assertTrue(f.clean('True'))
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('False')

    def test_booleanfield_clean_2(self):
        """
        Tests the clean method of a BooleanField.
        
        This function tests the clean method of a BooleanField to ensure it correctly handles various inputs and returns the expected boolean values. The field is not required.
        
        Parameters:
        - No specific parameters are passed to this function. It tests the clean method with different input values.
        
        Returns:
        - None: This function does not return anything. It is used for testing purposes.
        
        Test Cases:
        - An empty string is cleaned to False.
        - None is cleaned to False.
        -
        """

        f = BooleanField(required=False)
        self.assertIs(f.clean(''), False)
        self.assertIs(f.clean(None), False)
        self.assertIs(f.clean(True), True)
        self.assertIs(f.clean(False), False)
        self.assertIs(f.clean(1), True)
        self.assertIs(f.clean(0), False)
        self.assertIs(f.clean('1'), True)
        self.assertIs(f.clean('0'), False)
        self.assertIs(f.clean('Django rocks'), True)
        self.assertIs(f.clean('False'), False)
        self.assertIs(f.clean('false'), False)
        self.assertIs(f.clean('FaLsE'), False)

    def test_boolean_picklable(self):
        self.assertIsInstance(pickle.loads(pickle.dumps(BooleanField())), BooleanField)

    def test_booleanfield_changed(self):
        """
        Tests the `has_changed` method of the `BooleanField` class.
        
        This method checks if the field has changed from its initial value. The function tests various scenarios where the field might have changed or not, including:
        
        - When both initial and current values are `None`.
        - When both initial and current values are empty strings.
        - When the initial value is `False` and the current value is 'on'.
        - When the initial value is `True` and the current value is 'on'.
        """

        f = BooleanField()
        self.assertFalse(f.has_changed(None, None))
        self.assertFalse(f.has_changed(None, ''))
        self.assertFalse(f.has_changed('', None))
        self.assertFalse(f.has_changed('', ''))
        self.assertTrue(f.has_changed(False, 'on'))
        self.assertFalse(f.has_changed(True, 'on'))
        self.assertTrue(f.has_changed(True, ''))
        # Initial value may have mutated to a string due to show_hidden_initial (#19537)
        self.assertTrue(f.has_changed('False', 'on'))
        # HiddenInput widget sends string values for boolean but doesn't clean them in value_from_datadict
        self.assertFalse(f.has_changed(False, 'False'))
        self.assertFalse(f.has_changed(True, 'True'))
        self.assertTrue(f.has_changed(False, 'True'))
        self.assertTrue(f.has_changed(True, 'False'))

    def test_disabled_has_changed(self):
        f = BooleanField(disabled=True)
        self.assertIs(f.has_changed('True', 'False'), False)
