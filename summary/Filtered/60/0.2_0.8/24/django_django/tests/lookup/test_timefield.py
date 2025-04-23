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
        Tests the filtering of alarms by hour.
        
        This function asserts that the queryset returned by filtering alarms where the time's hour is 5 contains a single alarm with the time '05:30:00 (Early)'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The queryset returned by `Alarm.objects.filter(time__hour=5)` is equal to `['<Alarm: 05:30:00 (Early)>']` when ordered is set
        """

        self.assertQuerysetEqual(
            Alarm.objects.filter(time__hour=5),
            ['<Alarm: 05:30:00 (Early)>'],
            ordered=False
        )

    def test_minute_lookups(self):
        self.assertQuerysetEqual(
            Alarm.objects.filter(time__minute=30),
            ['<Alarm: 05:30:00 (Early)>'],
            ordered=False
        )

    def test_second_lookups(self):
        self.assertQuerysetEqual(
            Alarm.objects.filter(time__second=56),
            ['<Alarm: 12:34:56 (Precise)>'],
            ordered=False
        )
 of the time field.
        This function asserts that the queryset returned by filtering Alarm objects where the second component of the time is 56
        matches the expected result. The expected result is a queryset containing a single Alarm object with the time 12:34:56 (Precise).
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The queryset returned by filtering Alarm objects where the second component of the time is
        """

        self.assertQuerysetEqual(
            Alarm.objects.filter(time__second=56),
            ['<Alarm: 12:34:56 (Precise)>'],
            ordered=False
        )
