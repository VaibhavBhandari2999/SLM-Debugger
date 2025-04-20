from django.test import TestCase

from .models import Alarm


class TimeFieldLookupTests(TestCase):

    @classmethod
    def setUpTestData(self):
        """
        setUpTestData(self)
        
        This method is used to set up test data for the test cases. It creates a few Alarm objects with predefined descriptions and times.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Data Points:
        - self.al1: An Alarm object with description 'Early' and time '05:30'.
        - self.al2: An Alarm object with description 'Late' and time '10:00'.
        - self.al3: An Alarm object
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
        """
        Tests the filtering of alarms based on the minute component of their time.
        
        This function asserts that the queryset returned by filtering alarms where the minute component of the time is 30 matches the expected result.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The queryset returned by `Alarm.objects.filter(time__minute=30)` is equal to `['<Alarm: 05:30:00 (Early)>']` when evaluated using `assertQuerysetEqual`.
        """

        self.assertQuerysetEqual(
            Alarm.objects.filter(time__minute=30),
            ['<Alarm: 05:30:00 (Early)>'],
            ordered=False
        )

    def test_second_lookups(self):
        """
        Tests the filtering of Alarm objects based on the second component of the time field.
        
        This function asserts that the queryset returned by filtering Alarm objects where the second component of the time field is 56 matches the expected result.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Expected Output:
        - The queryset should contain one Alarm object with the time '12:34
        """

        self.assertQuerysetEqual(
            Alarm.objects.filter(time__second=56),
            ['<Alarm: 12:34:56 (Precise)>'],
            ordered=False
        )
