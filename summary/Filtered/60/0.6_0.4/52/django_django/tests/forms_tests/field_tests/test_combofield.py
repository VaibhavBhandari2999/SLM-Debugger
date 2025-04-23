from django.core.exceptions import ValidationError
from django.forms import CharField, ComboField, EmailField
from django.test import SimpleTestCase


class ComboFieldTest(SimpleTestCase):

    def test_combofield_1(self):
        """
        Tests the behavior of a ComboField with two fields: CharField and EmailField. The function validates the input based on the specified constraints.
        
        Parameters:
        - value (str): The value to be cleaned and validated.
        
        Returns:
        - str: The cleaned and validated email address if it passes all validations.
        - ValidationError: If the input does not meet the validation criteria.
        
        Key Points:
        - The ComboField is initialized with a CharField with a maximum length of 20 characters and an EmailField.
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
