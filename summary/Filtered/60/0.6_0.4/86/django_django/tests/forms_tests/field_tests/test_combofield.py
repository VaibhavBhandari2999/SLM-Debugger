from django.core.exceptions import ValidationError
from django.forms import CharField, ComboField, EmailField
from django.test import SimpleTestCase


class ComboFieldTest(SimpleTestCase):

    def test_combofield_1(self):
        """
        Tests the functionality of the ComboField with different inputs.
        
        This function tests the ComboField with various inputs to ensure it behaves as expected. The ComboField is tested with a combination of CharField and EmailField. The function checks the following scenarios:
        - Successful validation and cleaning of a valid email address.
        - Validation failure due to exceeding the maximum length for a CharField.
        - Validation failure due to an invalid email format.
        - Validation failure when the field is left empty.
        - Validation failure when the field
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
