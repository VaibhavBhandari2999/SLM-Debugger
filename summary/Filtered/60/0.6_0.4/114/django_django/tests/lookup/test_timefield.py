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
        Function: test_hour_lookups
        Summary: Tests the filtering of alarms based on the hour component of their time.
        
        Parameters:
        - self: The test case instance, used to interact with the test framework.
        
        Returns:
        - None: This function is a test case and does not return any value. It asserts the correctness of the filtering.
        
        Key Points:
        - The function uses the `assertSequenceEqual` method to check if the filtered queryset matches the expected result.
        - The `Alarm.objects.filter(time
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
        """
        Tests the filtering of alarms based on the second component of their time.
        
        This function checks if the Alarm objects with the time second component equal to 56 are correctly identified and returned.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The filtered Alarm objects should match the expected list containing only self.al3.
        """

        self.assertSequenceEqual(
            Alarm.objects.filter(time__second=56),
            [self.al3],
        )
