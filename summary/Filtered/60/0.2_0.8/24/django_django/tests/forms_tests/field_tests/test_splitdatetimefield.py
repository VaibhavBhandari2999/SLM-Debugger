import datetime

from django.forms import SplitDateTimeField, ValidationError
from django.forms.widgets import SplitDateTimeWidget
from django.test import SimpleTestCase


class SplitDateTimeFieldTest(SimpleTestCase):

    def test_splitdatetimefield_1(self):
        f = SplitDateTimeField()
        self.assertIsInstance(f.widget, SplitDateTimeWidget)
        self.assertEqual(
            datetime.datetime(2006, 1, 10, 7, 30),
            f.clean([datetime.date(2006, 1, 10), datetime.time(7, 30)])
        )
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'Enter a list of values.'"):
            f.clean('hello')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.', 'Enter a valid time.'"):
            f.clean(['hello', 'there'])
        with self.assertRaisesMessage(ValidationError, "'Enter a valid time.'"):
            f.clean(['2006-01-10', 'there'])
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean(['hello', '07:30'])

    def test_splitdatetimefield_2(self):
        f = SplitDateTimeField(required=False)
        self.assertEqual(
            datetime.datetime(2006, 1, 10, 7, 30),
            f.clean([datetime.date(2006, 1, 10), datetime.time(7, 30)])
        )
        self.assertEqual(datetime.datetime(2006, 1, 10, 7, 30), f.clean(['2006-01-10', '07:30']))
        self.assertIsNone(f.clean(None))
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(['']))
        self.assertIsNone(f.clean(['', '']))
        with self.assertRaisesMessage(ValidationError, "'Enter a list of values.'"):
            f.clean('hello')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.', 'Enter a valid time.'"):
            f.clean(['hello', 'there'])
        with self.assertRaisesMessage(ValidationError, "'Enter a valid time.'"):
            f.clean(['2006-01-10', 'there'])
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean(['hello', '07:30'])
        with self.assertRaisesMessage(ValidationError, "'Enter a valid time.'"):
            f.clean(['2006-01-10', ''])
        with self.assertRaisesMessage(ValidationError, "'Enter a valid time.'"):
            f.clean(['2006-01-10'])
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean(['', '07:30'])

    def test_splitdatetimefield_changed(self):
        """
        Tests the behavior of the SplitDateTimeField's has_changed method.
        
        Parameters:
        - input_date_formats (list): A list of date format strings used to parse input dates.
        
        Methods tested:
        - has_changed: Compares two sets of date and time values to determine if they have changed.
        
        Test cases:
        1. Checks if the field has not changed when both date and time values are the same.
        2. Verifies that the field detects a change when the date and time values are different.
        """

        f = SplitDateTimeField(input_date_formats=['%d/%m/%Y'])
        self.assertFalse(f.has_changed(['11/01/2012', '09:18:15'], ['11/01/2012', '09:18:15']))
        self.assertTrue(f.has_changed(datetime.datetime(2008, 5, 6, 12, 40, 00), ['2008-05-06', '12:40:00']))
        self.assertFalse(f.has_changed(datetime.datetime(2008, 5, 6, 12, 40, 00), ['06/05/2008', '12:40']))
        self.assertTrue(f.has_changed(datetime.datetime(2008, 5, 6, 12, 40, 00), ['06/05/2008', '12:41']))
atetime(2008, 5, 6, 12, 40, 00), ['06/05/2008', '12:41']))
