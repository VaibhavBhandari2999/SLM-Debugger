from django.core.exceptions import ValidationError
from django.forms import EmailField
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class EmailFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_emailfield_1(self):
        """
        Tests the behavior of the EmailField in a form.
        
        This function tests the EmailField to ensure it behaves as expected. It checks the rendering of the widget, validation of required fields, and validation of email formats, including internationalized domain names.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The EmailField is rendered as an input type of 'email' with required attribute.
        - An empty string or None value raises a ValidationError with the message "'This field is required.'".
        """

        f = EmailField()
        self.assertWidgetRendersTo(f, '<input type="email" name="f" id="id_f" required>')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual('person@example.com', f.clean('person@example.com'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid email address.'"):
            f.clean('foo')
        self.assertEqual(
            'local@domain.with.idn.xyz\xe4\xf6\xfc\xdfabc.part.com',
            f.clean('local@domain.with.idn.xyzäöüßabc.part.com')
        )

    def test_email_regexp_for_performance(self):
        f = EmailField()
        # Check for runaway regex security problem. This will take a long time
        # if the security fix isn't in place.
        addr = 'viewx3dtextx26qx3d@yahoo.comx26latlngx3d15854521645943074058'
        self.assertEqual(addr, f.clean(addr))

    def test_emailfield_not_required(self):
        f = EmailField(required=False)
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
        self.assertEqual('person@example.com', f.clean('person@example.com'))
        self.assertEqual('example@example.com', f.clean('      example@example.com  \t   \t '))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid email address.'"):
            f.clean('foo')

    def test_emailfield_min_max_length(self):
        """
        Tests the EmailField with specified min_length and max_length constraints.
        
        This function validates the EmailField with given minimum and maximum length requirements. It checks the rendering of the field in a widget, the validation of input values, and the error messages for invalid inputs.
        
        Parameters:
        - None (The function uses internal assertions and does not take any parameters).
        
        Key Points:
        - min_length (int): The minimum allowed length of the email value.
        - max_length (int): The maximum allowed length of the email
        """

        f = EmailField(min_length=10, max_length=15)
        self.assertWidgetRendersTo(
            f,
            '<input id="id_f" type="email" name="f" maxlength="15" minlength="10" required>',
        )
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at least 10 characters (it has 9).'"):
            f.clean('a@foo.com')
        self.assertEqual('alf@foo.com', f.clean('alf@foo.com'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at most 15 characters (it has 20).'"):
            f.clean('alf123456788@foo.com')

    def test_emailfield_strip_on_none_value(self):
        f = EmailField(required=False, empty_value=None)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))

    def test_emailfield_unable_to_set_strip_kwarg(self):
        msg = "__init__() got multiple values for keyword argument 'strip'"
        with self.assertRaisesMessage(TypeError, msg):
            EmailField(strip=False)
            EmailField(strip=False)
