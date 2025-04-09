import datetime

from django.core.exceptions import ValidationError
from django.forms import DurationField
from django.test import SimpleTestCase
from django.utils import translation
from django.utils.duration import duration_string

from . import FormFieldAssertionsMixin


class DurationFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_durationfield_clean(self):
        """
        Tests the `clean` method of the `DurationField` class.
        
        This method validates and converts various string representations of time durations into `datetime.timedelta` objects.
        
        Args:
        None (This is a test method, no arguments are passed).
        
        Returns:
        None (This method asserts the expected results using `self.assertEqual`).
        
        Important Functions:
        - `DurationField.clean`: Converts a string representation of a duration into a `datetime.timedelta` object.
        
        Key Inputs:
        -
        """

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
        Tests the validation of a DurationField for overflow conditions.
        
        This function checks if the DurationField raises a ValidationError when
        given an invalid number of days that exceeds the minimum or maximum
        allowed values. The validation message includes the minimum and maximum
        valid days, calculated using `datetime.timedelta.min.days` and
        `datetime.timedelta.max.days`.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input duration is out of the valid range
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
        Tests the overflow translation functionality for the DurationField clean method. This function checks if a ValidationError is raised when an invalid duration (exceeding the maximum days) is passed. The function uses the `datetime.timedelta` class to define the minimum and maximum number of days allowed. It overrides the language context to French ('fr') and expects to see a specific error message related to the validation failure.
        """

        msg = "Le nombre de jours doit être entre {min_days} et {max_days}.".format(
            min_days=datetime.timedelta.min.days,
            max_days=datetime.timedelta.max.days,
        )
        with translation.override('fr'):
            with self.assertRaisesMessage(ValidationError, msg):
                DurationField().clean('1000000000 00:00:00')

    def test_durationfield_render(self):
        """
        Tests the rendering of a DurationField widget with an initial value of 1 hour. The rendered HTML input element should have an ID of 'id_f', a type of 'text', a name of 'f', a value of '01:00:00', and be marked as required.
        """

        self.assertWidgetRendersTo(
            DurationField(initial=datetime.timedelta(hours=1)),
            '<input id="id_f" type="text" name="f" value="01:00:00" required>',
        )

    def test_durationfield_integer_value(self):
        f = DurationField()
        self.assertEqual(datetime.timedelta(0, 10800), f.clean(10800))

    def test_durationfield_prepare_value(self):
        """
        Prepare a value for storage.
        
        This method converts a `datetime.timedelta` object or a string to a
        formatted duration string using the `duration_string` function. It also
        returns the input value unchanged if it is a string, and returns None if
        the input value is None.
        
        Args:
        td (datetime.timedelta): A timedelta object representing a duration.
        
        Returns:
        str: A formatted duration string or the original input value.
        """

        field = DurationField()
        td = datetime.timedelta(minutes=15, seconds=30)
        self.assertEqual(field.prepare_value(td), duration_string(td))
        self.assertEqual(field.prepare_value('arbitrary'), 'arbitrary')
        self.assertIsNone(field.prepare_value(None))
