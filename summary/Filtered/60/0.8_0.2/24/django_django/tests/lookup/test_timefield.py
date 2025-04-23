from django.test import TestCase

from .models import Alarm


class TimeFieldLookupTests(TestCase):

    @classmethod
    def setUpTestData(self):
        """
        setUpTestData(self)
        
        This method is used to set up test data for the test cases. It creates a few Alarm objects and stores them as instance variables for later use in tests.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Data Points:
        - self.al1: An Alarm object with description 'Early' and time '05:30'.
        - self.al2: An Alarm object with description 'Late' and time '10:00'.
        - self.al3:
        """

        # Create a few Alarms
        self.al1 = Alarm.objects.create(desc='Early', time='05:30')
        self.al2 = Alarm.objects.create(desc='Late', time='10:00')
        self.al3 = Alarm.objects.create(desc='Precise', time='12:34:56')

    def test_hour_lookups(self):
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
        """
        Tests the filtering of Alarm objects based on the second component of the time field.
        This function asserts that the queryset returned by filtering Alarm objects where the second component of the time is 56
        matches the expected result. The expected result is a queryset containing a single Alarm object with the time 12:34:56.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The queryset returned by `Alarm.objects.filter(time__second=56)` is equal to
        """

        self.assertQuerysetEqual(
            Alarm.objects.filter(time__second=56),
            ['<Alarm: 12:34:56 (Precise)>'],
            ordered=False
        )
