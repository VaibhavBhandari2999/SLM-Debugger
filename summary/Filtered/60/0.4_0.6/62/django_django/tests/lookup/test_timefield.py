from django.test import TestCase

from .models import Alarm


class TimeFieldLookupTests(TestCase):

    @classmethod
    def setUpTestData(self):
        # Create a few Alarms
        self.al1 = Alarm.objects.create(desc='Early', time='05:30')
        self.al2 = Alarm.objects.create(desc='Late', time='10:00')
        self.al3 = Alarm.objects.create(desc='Precise', time='12:34:56')

    def test_hour_lookups(self):
        """
        Tests the filtering of alarms based on the hour component of their time.
        
        This function asserts that the queryset returned by filtering alarms where the hour component of the time is 5 is equal to a sequence containing only the alarm instance `self.al1`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Elements:
        - `Alarm.objects.filter(time__hour=5)`: Filters the Alarm objects where the hour component of the time is 5.
        - `[self.al1]`: The expected
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
