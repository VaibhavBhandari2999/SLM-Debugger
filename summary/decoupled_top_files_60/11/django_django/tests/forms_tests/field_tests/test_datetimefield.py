import datetime

from django.forms import DateTimeField, ValidationError
from django.test import SimpleTestCase


class DateTimeFieldTest(SimpleTestCase):

    def test_datetimefield_1(self):
        """
        Tests the DateTimeField clean method for various input formats and values.
        
        Parameters:
        - datetime.date: A date object to be converted to a datetime object.
        - datetime.datetime: A datetime object to be validated.
        - str: A string representing a date and/or time in various formats.
        
        Returns:
        - datetime.datetime: The validated and converted datetime object.
        
        Raises:
        - ValidationError: If the input cannot be converted to a valid datetime object.
        
        Test cases include:
        - Converting a date to a datetime with time
        """

        f = DateTimeField()
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean(datetime.date(2006, 10, 25)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean(datetime.datetime(2006, 10, 25, 14, 30)))
        self.assertEqual(
            datetime.datetime(2006, 10, 25, 14, 30, 59),
            f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59))
        )
        self.assertEqual(
            datetime.datetime(2006, 10, 25, 14, 30, 59, 200),
            f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59, 200))
        )
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45, 200), f.clean('2006-10-25 14:30:45.000200'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45, 200), f.clean('2006-10-25 14:30:45.0002'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45), f.clean('2006-10-25 14:30:45'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('2006-10-25 14:30:00'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('2006-10-25 14:30'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean('2006-10-25'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45, 200), f.clean('10/25/2006 14:30:45.000200'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45), f.clean('10/25/2006 14:30:45'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('10/25/2006 14:30:00'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('10/25/2006 14:30'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean('10/25/2006'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45, 200), f.clean('10/25/06 14:30:45.000200'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45), f.clean('10/25/06 14:30:45'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('10/25/06 14:30:00'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('10/25/06 14:30'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean('10/25/06'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date/time.'"):
            f.clean('hello')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date/time.'"):
            f.clean('2006-10-25 4:30 p.m.')

    def test_datetimefield_2(self):
        f = DateTimeField(input_formats=['%Y %m %d %I:%M %p'])
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean(datetime.date(2006, 10, 25)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean(datetime.datetime(2006, 10, 25, 14, 30)))
        self.assertEqual(
            datetime.datetime(2006, 10, 25, 14, 30, 59),
            f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59))
        )
        self.assertEqual(
            datetime.datetime(2006, 10, 25, 14, 30, 59, 200),
            f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59, 200))
        )
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('2006 10 25 2:30 PM'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date/time.'"):
            f.clean('2006-10-25 14:30:45')

    def test_datetimefield_3(self):
        """
        Test the behavior of the DateTimeField when cleaning None and empty string inputs.
        
        This function tests the DateTimeField with the `required=False` parameter to ensure that it correctly handles None and empty string inputs. It verifies that the clean method returns None for both inputs and that the representation of the cleaned value is 'None' in both cases.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The DateTimeField is instantiated with `required=False`.
        - The clean method is called with None and
        """

        f = DateTimeField(required=False)
        self.assertIsNone(f.clean(None))
        self.assertEqual('None', repr(f.clean(None)))
        self.assertIsNone(f.clean(''))
        self.assertEqual('None', repr(f.clean('')))

    def test_datetimefield_4(self):
        f = DateTimeField()
        # Test whitespace stripping behavior (#5714)
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45), f.clean(' 2006-10-25   14:30:45 '))
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean(' 2006-10-25 '))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45), f.clean(' 10/25/2006 14:30:45 '))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean(' 10/25/2006 14:30 '))
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean(' 10/25/2006 '))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45), f.clean(' 10/25/06 14:30:45 '))
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean(' 10/25/06 '))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date/time.'"):
            f.clean('   ')

    def test_datetimefield_5(self):
        f = DateTimeField(input_formats=['%Y.%m.%d %H:%M:%S.%f'])
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45, 200), f.clean('2006.10.25 14:30:45.0002'))

    def test_datetimefield_changed(self):
        format = '%Y %m %d %I:%M %p'
        f = DateTimeField(input_formats=[format])
        d = datetime.datetime(2006, 9, 17, 14, 30, 0)
        self.assertFalse(f.has_changed(d, '2006 09 17 2:30 PM'))
