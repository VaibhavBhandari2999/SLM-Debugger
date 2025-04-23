from django.test import TestCase

from .models import Alarm


class TimeFieldLookupTests(TestCase):
    @classmethod
    def setUpTestData(self):
        """
        setUpTestData(self)
        
        This method is used to set up test data for the test cases. It creates a few Alarm objects and stores them as instance variables.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - self.al1: An Alarm object with description "Early" and time "05:30".
        - self.al2: An Alarm object with description "Late" and time "10:00".
        - self.al3: An Alarm object
        """

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
        Tests the filtering of alarms based on the minute component of their time.
        
        This function asserts that the `Alarm` objects filtered by the `time__minute` field set to 30 are equal to the sequence containing only `self.al1`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        - `self`: The test case instance, used to access `self.al1` and `Alarm.objects.filter()`.
        
        Raises:
        AssertionError: If the filtered `Alarm` objects do not
        """

        self.assertSequenceEqual(
            Alarm.objects.filter(time__minute=30),
            [self.al1],
        )

    def test_second_lookups(self):
        self.assertSequenceEqual(
            Alarm.objects.filter(time__second=56),
            [self.al3],
        )
