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
        Tests the clean method of the DurationField.
        
        This function tests the clean method of the DurationField to ensure it correctly parses and validates duration strings. The method accepts a string representing a duration and returns a datetime.timedelta object.
        
        Parameters:
        value (str): The duration string to be cleaned.
        
        Returns:
        datetime.timedelta: The parsed duration as a datetime.timedelta object.
        
        Test Cases:
        - '30' should return a timedelta of 30 seconds.
        - '15:30
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
        msg = "Le nombre de jours doit être entre {min_days} et {max_days}.".format(
            min_days=datetime.timedelta.min.days,
            max_days=datetime.timedelta.max.days,
        )
        with translation.override('fr'):
            with self.assertRaisesMessage(ValidationError, msg):
                DurationField().clean('1000000000 00:00:00')

    def test_durationfield_render(self):
        """
        Tests the rendering of a DurationField widget. The function asserts that the widget renders correctly with an initial value of 1 hour. The input field is expected to have an id of 'id_f', a type of 'text', a name of 'f', and a required attribute. The value should be formatted as '01:00:00'.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: The function asserts the expected output and does not return any value
        """

        self.assertWidgetRendersTo(
            DurationField(initial=datetime.timedelta(hours=1)),
            '<input id="id_f" type="text" name="f" value="01:00:00" required>',
        )

    def test_durationfield_integer_value(self):
        f = DurationField()
        self.assertEqual(datetime.timedelta(0, 10800), f.clean(10800))

    def test_durationfield_prepare_value(self):
        field = DurationField()
        td = datetime.timedelta(minutes=15, seconds=30)
        self.assertEqual(field.prepare_value(td), duration_string(td))
        self.assertEqual(field.prepare_value('arbitrary'), 'arbitrary')
        self.assertIsNone(field.prepare_value(None))
