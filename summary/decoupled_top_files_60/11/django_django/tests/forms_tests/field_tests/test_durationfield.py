import datetime

from django.core.exceptions import ValidationError
from django.forms import DurationField
from django.test import SimpleTestCase
from django.utils import translation
from django.utils.duration import duration_string

from . import FormFieldAssertionsMixin


class DurationFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_durationfield_clean(self):
        f = DurationField()
        self.assertEqual(datetime.timedelta(seconds=30), f.clean('30'))
        self.assertEqual(datetime.timedelta(minutes=15, seconds=30), f.clean('15:30'))
        self.assertEqual(datetime.timedelta(hours=1, minutes=15, seconds=30), f.clean('1:15:30'))
        self.assertEqual(
            datetime.timedelta(days=1, hours=1, minutes=15, seconds=30, milliseconds=300),
            f.clean('1 1:15:30.3')
        )

    def test_overflow(self):
        """
        Tests the validation of a DurationField to ensure it raises a ValidationError when the input exceeds the allowed range of days. The function uses the `datetime.timedelta` class to define the minimum and maximum number of days allowed. It checks both positive and negative overflow cases.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input exceeds the allowed range of days.
        
        Example Usage:
        test_overflow()
        """

        msg = "The number of days must be between {min_days} and {max_days}.".format(
            min_days=datetime.timedelta.min.days,
            max_days=datetime.timedelta.max.days,
        )
        f = DurationField()
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('1000000000 00:00:00')
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('-1000000000 00:00:00')

    def test_overflow_translation(self):
        """
        Tests the overflow validation for the DurationField.
        
        This function tests the validation of a duration field to ensure that it raises a ValidationError when the number of days exceeds the maximum allowed by the datetime.timedelta type. The test is performed in French language context.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses the `translation.override` context manager to set the language to French.
        - It constructs a validation error message using `datetime.timedelta.min.days` and `datetime.timedelta.max.days
        """

        msg = "Le nombre de jours doit être entre {min_days} et {max_days}.".format(
            min_days=datetime.timedelta.min.days,
            max_days=datetime.timedelta.max.days,
        )
        with translation.override('fr'):
            with self.assertRaisesMessage(ValidationError, msg):
                DurationField().clean('1000000000 00:00:00')

    def test_durationfield_render(self):
        self.assertWidgetRendersTo(
            DurationField(initial=datetime.timedelta(hours=1)),
            '<input id="id_f" type="text" name="f" value="01:00:00" required>',
        )

    def test_durationfield_integer_value(self):
        f = DurationField()
        self.assertEqual(datetime.timedelta(0, 10800), f.clean(10800))

    def test_durationfield_prepare_value(self):
        """
        Tests the `prepare_value` method of the `DurationField` class.
        
        This method is responsible for converting various input types into a standardized form. The function checks the following scenarios:
        - Converts a `datetime.timedelta` object into a string representation using the `duration_string` function.
        - Returns the input value unchanged if it is a string.
        - Returns `None` if the input value is `None`.
        
        Parameters:
        - field: An instance of `DurationField` used for the conversion process.
        -
        """

        field = DurationField()
        td = datetime.timedelta(minutes=15, seconds=30)
        self.assertEqual(field.prepare_value(td), duration_string(td))
        self.assertEqual(field.prepare_value('arbitrary'), 'arbitrary')
        self.assertIsNone(field.prepare_value(None))
