from django.core.exceptions import ValidationError
from django.forms import CharField, ComboField, EmailField
from django.test import SimpleTestCase


class ComboFieldTest(SimpleTestCase):

    def test_combofield_1(self):
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
        - No explicit parameters are passed to the function, but it assumes the existence of a ComboField instance 'f' with the specified fields.
        
        Returns:
        - None
        
        Key Behaviors:
        - Validates and cleans an email address, ensuring it is within the specified length and is a valid email.
        - Raises ValidationError if the input does not meet the criteria for either field.
        """

        f = ComboField(fields=[CharField(max_length=20), EmailField()], required=False)
        self.assertEqual('test@example.com', f.clean('test@example.com'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at most 20 characters (it has 28).'"):
            f.clean('longemailaddress@example.com')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid email address.'"):
            f.clean('not an email')
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
