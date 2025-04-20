import unittest
from datetime import date, datetime, time, timedelta

from django.utils.dateparse import (
    parse_date, parse_datetime, parse_duration, parse_time,
)
from django.utils.timezone import get_fixed_timezone


class DateParseTests(unittest.TestCase):

    def test_parse_date(self):
        """
        Function to parse a date string into a Python `date` object.
        
        Args:
        date_str (str): A date string in the format 'YYYY-MM-DD' or 'YYYY-M-D'.
        
        Returns:
        date: A `date` object representing the parsed date, or None if the input is invalid.
        
        Raises:
        ValueError: If the date string is in an invalid format or contains invalid date values.
        
        Examples:
        >>> parse_date('2012-04-23')
        """

        # Valid inputs
        self.assertEqual(parse_date('2012-04-23'), date(2012, 4, 23))
        self.assertEqual(parse_date('2012-4-9'), date(2012, 4, 9))
        # Invalid inputs
        self.assertIsNone(parse_date('20120423'))
        with self.assertRaises(ValueError):
            parse_date('2012-04-56')

    def test_parse_time(self):
        # Valid inputs
        self.assertEqual(parse_time('09:15:00'), time(9, 15))
        self.assertEqual(parse_time('10:10'), time(10, 10))
        self.assertEqual(parse_time('10:20:30.400'), time(10, 20, 30, 400000))
        self.assertEqual(parse_time('4:8:16'), time(4, 8, 16))
        # Invalid inputs
        self.assertIsNone(parse_time('091500'))
        with self.assertRaises(ValueError):
            parse_time('09:15:90')

    def test_parse_datetime(self):
        valid_inputs = (
            ('2012-04-23T09:15:00', datetime(2012, 4, 23, 9, 15)),
            ('2012-4-9 4:8:16', datetime(2012, 4, 9, 4, 8, 16)),
            ('2012-04-23T09:15:00Z', datetime(2012, 4, 23, 9, 15, 0, 0, get_fixed_timezone(0))),
            ('2012-4-9 4:8:16-0320', datetime(2012, 4, 9, 4, 8, 16, 0, get_fixed_timezone(-200))),
            ('2012-04-23T10:20:30.400+02:30', datetime(2012, 4, 23, 10, 20, 30, 400000, get_fixed_timezone(150))),
            ('2012-04-23T10:20:30.400+02', datetime(2012, 4, 23, 10, 20, 30, 400000, get_fixed_timezone(120))),
            ('2012-04-23T10:20:30.400-02', datetime(2012, 4, 23, 10, 20, 30, 400000, get_fixed_timezone(-120))),
        )
        for source, expected in valid_inputs:
            with self.subTest(source=source):
                self.assertEqual(parse_datetime(source), expected)

        # Invalid inputs
        self.assertIsNone(parse_datetime('20120423091500'))
        with self.assertRaises(ValueError):
            parse_datetime('2012-04-56T09:15:90')


class DurationParseTests(unittest.TestCase):

    def test_parse_python_format(self):
        """
        Tests the `parse_duration` function by parsing various timedelta objects and comparing them to the original timedelta values.
        
        Parameters:
        - timedeltas (list): A list of `timedelta` objects representing different durations.
        
        Returns:
        - None: The function uses assertions to verify that the parsed duration matches the original timedelta.
        
        Key Test Cases:
        1. Fractions of seconds: `timedelta(days=4, minutes=15, seconds=30, milliseconds=100)`
        2. Hours, minutes
        """

        timedeltas = [
            timedelta(days=4, minutes=15, seconds=30, milliseconds=100),  # fractions of seconds
            timedelta(hours=10, minutes=15, seconds=30),  # hours, minutes, seconds
            timedelta(days=4, minutes=15, seconds=30),  # multiple days
            timedelta(days=1, minutes=00, seconds=00),  # single day
            timedelta(days=-4, minutes=15, seconds=30),  # negative durations
            timedelta(minutes=15, seconds=30),  # minute & seconds
            timedelta(seconds=30),  # seconds
        ]
        for delta in timedeltas:
            with self.subTest(delta=delta):
                self.assertEqual(parse_duration(format(delta)), delta)

    def test_parse_postgresql_format(self):
        test_values = (
            ('1 day', timedelta(1)),
            ('1 day 0:00:01', timedelta(days=1, seconds=1)),
            ('1 day -0:00:01', timedelta(days=1, seconds=-1)),
            ('-1 day -0:00:01', timedelta(days=-1, seconds=-1)),
            ('-1 day +0:00:01', timedelta(days=-1, seconds=1)),
            ('4 days 0:15:30.1', timedelta(days=4, minutes=15, seconds=30, milliseconds=100)),
            ('4 days 0:15:30.0001', timedelta(days=4, minutes=15, seconds=30, microseconds=100)),
            ('-4 days -15:00:30', timedelta(days=-4, hours=-15, seconds=-30)),
        )
        for source, expected in test_values:
            with self.subTest(source=source):
                self.assertEqual(parse_duration(source), expected)

    def test_seconds(self):
        self.assertEqual(parse_duration('30'), timedelta(seconds=30))

    def test_minutes_seconds(self):
        self.assertEqual(parse_duration('15:30'), timedelta(minutes=15, seconds=30))
        self.assertEqual(parse_duration('5:30'), timedelta(minutes=5, seconds=30))

    def test_hours_minutes_seconds(self):
        self.assertEqual(parse_duration('10:15:30'), timedelta(hours=10, minutes=15, seconds=30))
        self.assertEqual(parse_duration('1:15:30'), timedelta(hours=1, minutes=15, seconds=30))
        self.assertEqual(parse_duration('100:200:300'), timedelta(hours=100, minutes=200, seconds=300))

    def test_days(self):
        self.assertEqual(parse_duration('4 15:30'), timedelta(days=4, minutes=15, seconds=30))
        self.assertEqual(parse_duration('4 10:15:30'), timedelta(days=4, hours=10, minutes=15, seconds=30))

    def test_fractions_of_seconds(self):
        """
        Tests the parsing of duration strings with fractions of seconds.
        
        This function tests the `parse_duration` function by comparing the parsed `timedelta` objects against expected values. The test cases include durations with milliseconds and microseconds.
        
        Parameters:
        None
        
        Returns:
        None
        
        Test Cases:
        - '15:30.1' should be parsed as `timedelta(minutes=15, seconds=30, milliseconds=100)`
        - '15:30.01'
        """

        test_values = (
            ('15:30.1', timedelta(minutes=15, seconds=30, milliseconds=100)),
            ('15:30.01', timedelta(minutes=15, seconds=30, milliseconds=10)),
            ('15:30.001', timedelta(minutes=15, seconds=30, milliseconds=1)),
            ('15:30.0001', timedelta(minutes=15, seconds=30, microseconds=100)),
            ('15:30.00001', timedelta(minutes=15, seconds=30, microseconds=10)),
            ('15:30.000001', timedelta(minutes=15, seconds=30, microseconds=1)),
        )
        for source, expected in test_values:
            with self.subTest(source=source):
                self.assertEqual(parse_duration(source), expected)

    def test_negative(self):
        test_values = (
            ('-4 15:30', timedelta(days=-4, minutes=15, seconds=30)),
            ('-172800', timedelta(days=-2)),
            ('-15:30', timedelta(minutes=-15, seconds=-30)),
            ('-1:15:30', timedelta(hours=-1, minutes=-15, seconds=-30)),
            ('-30.1', timedelta(seconds=-30, milliseconds=-100)),
            ('-00:01:01', timedelta(minutes=-1, seconds=-1)),
            ('-01:01', timedelta(seconds=-61)),
            ('-01:-01', None),
        )
        for source, expected in test_values:
            with self.subTest(source=source):
                self.assertEqual(parse_duration(source), expected)

    def test_iso_8601(self):
        """
        Function to test ISO 8601 duration strings.
        
        This function tests the parsing of ISO 8601 duration strings into Python timedelta objects.
        
        Parameters:
        source (str): The ISO 8601 duration string to be parsed.
        expected (timedelta or None): The expected timedelta object or None if no timedelta is expected.
        
        Returns:
        None: The function asserts that the parsed timedelta matches the expected value.
        
        Test Cases:
        - 'P4Y': No expected
        """

        test_values = (
            ('P4Y', None),
            ('P4M', None),
            ('P4W', None),
            ('P4D', timedelta(days=4)),
            ('P0.5D', timedelta(hours=12)),
            ('PT5H', timedelta(hours=5)),
            ('PT5M', timedelta(minutes=5)),
            ('PT5S', timedelta(seconds=5)),
            ('PT0.000005S', timedelta(microseconds=5)),
        )
        for source, expected in test_values:
            with self.subTest(source=source):
                self.assertEqual(parse_duration(source), expected)
