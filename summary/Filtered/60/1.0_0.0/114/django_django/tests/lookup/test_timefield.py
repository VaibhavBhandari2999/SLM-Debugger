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
        self.assertSequenceEqual(
            Alarm.objects.filter(time__hour=5),
            [self.al1],
        )

    def test_minute_lookups(self):
        """
        Tests the filtering of alarms based on the 'minute' attribute of their time.
        
        This function asserts that the query to filter alarms where the 'minute' attribute of the 'time' field is equal to 30 returns the expected result.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The result of the query `Alarm.objects.filter(time__minute=30)` should be a sequence containing only the alarm `self.al1`.
        """

        self.assertSequenceEqual(
            Alarm.objects.filter(time__minute=30),
            [self.al1],
        )

    def test_second_lookups(self):
        """
        Tests the ability to filter alarms based on the second component of their time.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The result of filtering alarms by time__second equal to 56 should match the list containing only self.al3.
        """

        self.assertSequenceEqual(
            Alarm.objects.filter(time__second=56),
            [self.al3],
        )
