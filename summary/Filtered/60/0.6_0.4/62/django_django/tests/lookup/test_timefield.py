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
        - self.al3: An Alarm object with description '
        """

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
        self.assertSequenceEqual(
            Alarm.objects.filter(time__minute=30),
            [self.al1],
        )

    def test_second_lookups(self):
        self.assertSequenceEqual(
            Alarm.objects.filter(time__second=56),
            [self.al3],
        )
