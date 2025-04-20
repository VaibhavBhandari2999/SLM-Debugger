from django.forms import CharField, ComboField, EmailField, ValidationError
from django.test import SimpleTestCase


class ComboFieldTest(SimpleTestCase):

    def test_combofield_1(self):
        """
        Tests the behavior of a ComboField with two fields: a CharField with a maximum length of 20 characters and an EmailField.
        
        Parameters:
        - None (This function uses internal test assertions and does not take any parameters)
        
        Returns:
        - None (This function performs validation tests and does not return any value)
        
        Key Behaviors:
        - Validates an email address ('test@example.com') and passes the test.
        - Validates a long email address ('longemailaddress@example.com') and raises a ValidationError with
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
        - No explicit parameters are needed for this test function.
        
        Returns:
        - None
        
        Key Behaviors:
        - Validates and cleans an email address if provided.
        - Ensures the email address does not exceed 20 characters.
        - Validates the email format.
        - Handles empty or None inputs gracefully.
        
        Raises:
        - ValidationError: If the input is not a valid email or exceeds the character
        """

        f = ComboField(fields=[CharField(max_length=20), EmailField()], required=False)
        self.assertEqual('test@example.com', f.clean('test@example.com'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at most 20 characters (it has 28).'"):
            f.clean('longemailaddress@example.com')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid email address.'"):
            f.clean('not an email')
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
