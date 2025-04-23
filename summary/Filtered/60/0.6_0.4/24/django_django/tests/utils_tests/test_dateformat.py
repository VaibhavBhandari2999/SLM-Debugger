from datetime import date, datetime

from django.test import SimpleTestCase, override_settings
from django.test.utils import TZ_SUPPORT, requires_tz_support
from django.utils import dateformat, translation
from django.utils.dateformat import format
from django.utils.timezone import (
    get_default_timezone, get_fixed_timezone, make_aware, utc,
)


@override_settings(TIME_ZONE='Europe/Copenhagen')
class DateFormatTests(SimpleTestCase):

    def setUp(self):
        self._orig_lang = translation.get_language()
        translation.activate('en-us')

    def tearDown(self):
        translation.activate(self._orig_lang)

    def test_date(self):
        d = date(2009, 5, 16)
        self.assertEqual(date.fromtimestamp(int(format(d, 'U'))), d)

    def test_naive_datetime(self):
        dt = datetime(2009, 5, 16, 5, 30, 30)
        self.assertEqual(datetime.fromtimestamp(int(format(dt, 'U'))), dt)

    def test_naive_ambiguous_datetime(self):
        """
        Tests the behavior of datetime formatters in the presence of ambiguous times.
        
        This function tests how the datetime formatters behave when given a datetime
        object that is ambiguous in the timezone 'Europe/Copenhagen'. The datetime
        object is set to October 25, 2015, at 2:30 AM. The formatters 'I', 'O', 'T',
        and 'Z' are used to format the datetime object. Since the datetime is
        ambiguous, the formatters
        """

        # dt is ambiguous in Europe/Copenhagen. pytz raises an exception for
        # the ambiguity, which results in an empty string.
        dt = datetime(2015, 10, 25, 2, 30, 0)

        # Try all formatters that involve self.timezone.
        self.assertEqual(format(dt, 'I'), '')
        self.assertEqual(format(dt, 'O'), '')
        self.assertEqual(format(dt, 'T'), '')
        self.assertEqual(format(dt, 'Z'), '')

    @requires_tz_support
    def test_datetime_with_local_tzinfo(self):
        ltz = get_default_timezone()
        dt = make_aware(datetime(2009, 5, 16, 5, 30, 30), ltz)
        self.assertEqual(datetime.fromtimestamp(int(format(dt, 'U')), ltz), dt)
        self.assertEqual(datetime.fromtimestamp(int(format(dt, 'U'))), dt.replace(tzinfo=None))

    @requires_tz_support
    def test_datetime_with_tzinfo(self):
        """
        Tests the behavior of datetime objects with timezone information.
        
        This function checks the conversion and manipulation of datetime objects with timezone information. It creates a timezone object and a datetime object with a specific timezone. The function then verifies the following:
        - The datetime object is correctly converted to a timezone with a fixed offset (-510 minutes).
        - The datetime object is correctly converted to the default timezone.
        - The astimezone() method is used to safely convert the datetime object to the default timezone without affecting its original
        """

        tz = get_fixed_timezone(-510)
        ltz = get_default_timezone()
        dt = make_aware(datetime(2009, 5, 16, 5, 30, 30), ltz)
        self.assertEqual(datetime.fromtimestamp(int(format(dt, 'U')), tz), dt)
        self.assertEqual(datetime.fromtimestamp(int(format(dt, 'U')), ltz), dt)
        # astimezone() is safe here because the target timezone doesn't have DST
        self.assertEqual(datetime.fromtimestamp(int(format(dt, 'U'))), dt.astimezone(ltz).replace(tzinfo=None))
        self.assertEqual(datetime.fromtimestamp(int(format(dt, 'U')), tz).utctimetuple(), dt.utctimetuple())
        self.assertEqual(datetime.fromtimestamp(int(format(dt, 'U')), ltz).utctimetuple(), dt.utctimetuple())

    def test_epoch(self):
        udt = datetime(1970, 1, 1, tzinfo=utc)
        self.assertEqual(format(udt, 'U'), '0')

    def test_empty_format(self):
        my_birthday = datetime(1979, 7, 8, 22, 00)

        self.assertEqual(dateformat.format(my_birthday, ''), '')

    def test_am_pm(self):
        my_birthday = datetime(1979, 7, 8, 22, 00)

        self.assertEqual(dateformat.format(my_birthday, 'a'), 'p.m.')

    def test_microsecond(self):
        # Regression test for #18951
        dt = datetime(2009, 5, 16, microsecond=123)
        self.assertEqual(dateformat.format(dt, 'u'), '000123')

    def test_date_formats(self):
        my_birthday = datetime(1979, 7, 8, 22, 00)
        timestamp = datetime(2008, 5, 19, 11, 45, 23, 123456)

        self.assertEqual(dateformat.format(my_birthday, 'A'), 'PM')
        self.assertEqual(dateformat.format(timestamp, 'c'), '2008-05-19T11:45:23.123456')
        self.assertEqual(dateformat.format(my_birthday, 'd'), '08')
        self.assertEqual(dateformat.format(my_birthday, 'j'), '8')
        self.assertEqual(dateformat.format(my_birthday, 'l'), 'Sunday')
        self.assertEqual(dateformat.format(my_birthday, 'L'), 'False')
        self.assertEqual(dateformat.format(my_birthday, 'm'), '07')
        self.assertEqual(dateformat.format(my_birthday, 'M'), 'Jul')
        self.assertEqual(dateformat.format(my_birthday, 'b'), 'jul')
        self.assertEqual(dateformat.format(my_birthday, 'n'), '7')
        self.assertEqual(dateformat.format(my_birthday, 'N'), 'July')

    def test_time_formats(self):
        """
        Tests the date format functionality of the dateformat module.
        
        This function tests various date format options for a given datetime object. The datetime object represents the user's birthday on July 8, 1979, at 10 p.m.
        
        Parameters:
        None
        
        Returns:
        None
        
        Test Cases:
        - 'P' format: Should return '10 p.m.'
        - 's' format: Should return '00'
        - 'S' format: Should return
        """

        my_birthday = datetime(1979, 7, 8, 22, 00)

        self.assertEqual(dateformat.format(my_birthday, 'P'), '10 p.m.')
        self.assertEqual(dateformat.format(my_birthday, 's'), '00')
        self.assertEqual(dateformat.format(my_birthday, 'S'), 'th')
        self.assertEqual(dateformat.format(my_birthday, 't'), '31')
        self.assertEqual(dateformat.format(my_birthday, 'w'), '0')
        self.assertEqual(dateformat.format(my_birthday, 'W'), '27')
        self.assertEqual(dateformat.format(my_birthday, 'y'), '79')
        self.assertEqual(dateformat.format(my_birthday, 'Y'), '1979')
        self.assertEqual(dateformat.format(my_birthday, 'z'), '189')

    def test_dateformat(self):
        my_birthday = datetime(1979, 7, 8, 22, 00)

        self.assertEqual(dateformat.format(my_birthday, r'Y z \C\E\T'), '1979 189 CET')

        self.assertEqual(dateformat.format(my_birthday, r'jS \o\f F'), '8th of July')

    def test_futuredates(self):
        the_future = datetime(2100, 10, 25, 0, 00)
        self.assertEqual(dateformat.format(the_future, r'Y'), '2100')

    def test_timezones(self):
        my_birthday = datetime(1979, 7, 8, 22, 00)
        summertime = datetime(2005, 10, 30, 1, 00)
        wintertime = datetime(2005, 10, 30, 4, 00)
        timestamp = datetime(2008, 5, 19, 11, 45, 23, 123456)

        # 3h30m to the west of UTC
        tz = get_fixed_timezone(-210)
        aware_dt = datetime(2009, 5, 16, 5, 30, 30, tzinfo=tz)

        if TZ_SUPPORT:
            self.assertEqual(dateformat.format(my_birthday, 'O'), '+0100')
            self.assertEqual(dateformat.format(my_birthday, 'r'), 'Sun, 8 Jul 1979 22:00:00 +0100')
            self.assertEqual(dateformat.format(my_birthday, 'T'), 'CET')
            self.assertEqual(dateformat.format(my_birthday, 'e'), '')
            self.assertEqual(dateformat.format(aware_dt, 'e'), '-0330')
            self.assertEqual(dateformat.format(my_birthday, 'U'), '300315600')
            self.assertEqual(dateformat.format(timestamp, 'u'), '123456')
            self.assertEqual(dateformat.format(my_birthday, 'Z'), '3600')
            self.assertEqual(dateformat.format(summertime, 'I'), '1')
            self.assertEqual(dateformat.format(summertime, 'O'), '+0200')
            self.assertEqual(dateformat.format(wintertime, 'I'), '0')
            self.assertEqual(dateformat.format(wintertime, 'O'), '+0100')

        # Ticket #16924 -- We don't need timezone support to test this
        self.assertEqual(dateformat.format(aware_dt, 'O'), '-0330')

    def test_invalid_time_format_specifiers(self):
        """
        Tests the behavior of dateformat.format() when invalid time format specifiers are used.
        
        This function iterates through a list of invalid time format specifiers and checks if a TypeError is raised when attempting to format a date object with these specifiers. The expected error message is also verified.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If an invalid time format specifier is used in the dateformat.format() function.
        
        Key format specifiers tested:
        - 'a': Represents the
        """

        my_birthday = date(1984, 8, 7)

        for specifier in ['a', 'A', 'f', 'g', 'G', 'h', 'H', 'i', 'P', 's', 'u']:
            msg = (
                "The format for date objects may not contain time-related "
                "format specifiers (found '%s')." % specifier
            )
            with self.assertRaisesMessage(TypeError, msg):
                dateformat.format(my_birthday, specifier)
at.format(my_birthday, specifier)
