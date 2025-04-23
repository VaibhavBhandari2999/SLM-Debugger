from django.test import TestCase

from .models import Alarm


class TimeFieldLookupTests(TestCase):
    @classmethod
    def setUpTestData(self):
        # Create a few Alarms
        self.al1 = Alarm.objects.create(desc="Early", time="05:30")
        self.al2 = Alarm.objects.create(desc="Late", time="10:00")
        self.al3 = Alarm.objects.create(desc="Precise", time="12:34:56")

    def test_hour_lookups(self):
        """
        Tests the filtering of alarms by hour.
        
        This function asserts that the `Alarm` objects filtered by the `time__hour` field set to 5 are equal to the sequence containing only `self.al1`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the filtered `Alarm` objects do not match the expected sequence.
        """

        self.assertSequenceEqual(
            Alarm.objects.filter(time__hour=5),
            [self.al1],
        )

    def test_minute_lookups(self):
        self.assertSequenceEqual(
            Alarm.objects.filter(time__minute=30),
            [self.al1],
        )

    def test_second_lookups(self):
        self.assertSequenceEqual(
            Alarm.objects.filter(time__second=56),
            [self.al3],
        )
