from django.forms import CharField, ComboField, EmailField, ValidationError
from django.test import SimpleTestCase


class ComboFieldTest(SimpleTestCase):

    def test_combofield_1(self):
        """
        Tests the behavior of the ComboField with different inputs.
        
        This function tests the ComboField, which is a custom field that can handle multiple types of fields. It checks the following scenarios:
        - Valid email address: 'test@example.com' should be cleaned and returned as is.
        - Long email address: 'longemailaddress@example.com' should raise a ValidationError with the message indicating the maximum length.
        - Invalid email address: 'not an email' should raise a ValidationError with the message indicating an invalid email
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
        f = ComboField(fields=[CharField(max_length=20), EmailField()], required=False)
        self.assertEqual('test@example.com', f.clean('test@example.com'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at most 20 characters (it has 28).'"):
            f.clean('longemailaddress@example.com')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid email address.'"):
            f.clean('not an email')
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
