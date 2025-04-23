from django.core.exceptions import ValidationError
from django.forms import CharField, ComboField, EmailField
from django.test import SimpleTestCase


class ComboFieldTest(SimpleTestCase):

    def test_combofield_1(self):
        """
        Tests the behavior of a ComboField with two fields: CharField and EmailField.
        Parameters:
        - self: The test case instance.
        Key Methods:
        - clean: Validates and cleans input values for the ComboField.
        Input:
        - A string value to be cleaned by the ComboField.
        Output:
        - The cleaned value if valid.
        Raises:
        - ValidationError: If the input value is invalid according to the validation rules of the fields.
        Examples:
        - 'test@example.com' is a valid email and should
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
        - None (The test function does not take any parameters)
        
        Returns:
        - None (The function performs assertions and validations, but does not return any value)
        
        Key Behaviors:
        - Validates and cleans an email address if provided.
        - Ensures the email address does not exceed 20 characters.
        - Validates the email format.
        - Cleans and accepts an empty string or
        """

        f = ComboField(fields=[CharField(max_length=20), EmailField()], required=False)
        self.assertEqual('test@example.com', f.clean('test@example.com'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at most 20 characters (it has 28).'"):
            f.clean('longemailaddress@example.com')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid email address.'"):
            f.clean('not an email')
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
