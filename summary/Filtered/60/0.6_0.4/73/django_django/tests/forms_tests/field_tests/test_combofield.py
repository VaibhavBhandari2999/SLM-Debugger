from django.core.exceptions import ValidationError
from django.forms import CharField, ComboField, EmailField
from django.test import SimpleTestCase


class ComboFieldTest(SimpleTestCase):

    def test_combofield_1(self):
        """
        Tests the behavior of a ComboField with two fields: CharField and EmailField. The function validates the input based on the specified rules and raises ValidationError with appropriate messages for invalid inputs.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Behaviors:
        - Validates a valid email address and returns it.
        - Raises ValidationError if the email address is too long.
        - Raises ValidationError if the input is not a valid email address.
        - Raises ValidationError if the input is empty or None.
        """

        f = ComboField(fields=[CharField(max_length=20), EmailField()])
        self.assertEqual('test@example.com', f.clean('test@example.com'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at most 20 characters (it has 28).'"):
            f.clean('longemailaddress@example.com')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid email address.'"):
            f.clean('not an email')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)

    def test_combofield_2(self):
        """
        Tests the behavior of a ComboField with two fields: CharField and EmailField. The field is not required.
        
        Parameters:
        - No explicit parameters are passed to the function, but it relies on the ComboField instance `f` which is defined within the test method.
        
        Returns:
        - None: The function is a test method and does not return any value.
        
        Key Behaviors:
        - Validates and cleans a valid email address ('test@example.com').
        - Raises ValidationError for an email address that exceeds the maximum
        """

        f = ComboField(fields=[CharField(max_length=20), EmailField()], required=False)
        self.assertEqual('test@example.com', f.clean('test@example.com'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at most 20 characters (it has 28).'"):
            f.clean('longemailaddress@example.com')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid email address.'"):
            f.clean('not an email')
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
