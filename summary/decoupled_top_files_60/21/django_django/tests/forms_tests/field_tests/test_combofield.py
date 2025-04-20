from django.forms import CharField, ComboField, EmailField, ValidationError
from django.test import SimpleTestCase


class ComboFieldTest(SimpleTestCase):

    def test_combofield_1(self):
        """
        Tests the behavior of a ComboField with two fields: CharField and EmailField.
        The function validates the following:
        - It should correctly clean an email address with a valid email format and within the specified length.
        - It should raise a ValidationError if the email address exceeds the maximum length.
        - It should raise a ValidationError if the input is not a valid email address.
        - It should raise a ValidationError if the field is left empty or is None.
        
        Parameters:
        - No external parameters are passed to this function
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
        Tests the behavior of a ComboField with two fields: CharField and EmailField. The field is optional (required=False).
        
        Parameters:
        - No explicit parameters are passed to the function, but it relies on the ComboField instance `f` which is defined within the function.
        
        Key Behaviors:
        - Validates and cleans an email address if provided.
        - Ensures the email address does not exceed 20 characters.
        - Validates the email format.
        - Handles empty and None inputs by returning an empty string
        """

        f = ComboField(fields=[CharField(max_length=20), EmailField()], required=False)
        self.assertEqual('test@example.com', f.clean('test@example.com'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at most 20 characters (it has 28).'"):
            f.clean('longemailaddress@example.com')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid email address.'"):
            f.clean('not an email')
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
