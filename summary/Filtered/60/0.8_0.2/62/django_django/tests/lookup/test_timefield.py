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
        self.assertSequenceEqual(
            Alarm.objects.filter(time__hour=5),
            [self.al1],
        )

    def test_minute_lookups(self):
        """
        Tests the filtering of alarms based on the minute component of their time.
        
        This function asserts that the `Alarm` objects filtered by the `time__minute` field set to 30 match the expected list containing only `self.al1`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        - `Alarm`: The model class for alarm objects.
        - `time__minute`: The lookup parameter used to filter alarms by their minute.
        - `self.al1`: An instance of
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
 
y to filter alarms where the second component of the time is 56 returns the expected alarm object.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The filtered query set should contain exactly one alarm object, which is self.al3.
        """

        self.assertSequenceEqual(
            Alarm.objects.filter(time__second=56),
            [self.al3],
        )
