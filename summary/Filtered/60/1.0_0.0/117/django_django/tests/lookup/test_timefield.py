from django.test import TestCase

from .models import Alarm


class TimeFieldLookupTests(TestCase):
    @classmethod
    def setUpTestData(self):
        """
        setUpTestData(self)
        This method sets up test data for use in testing. It creates a few Alarm objects and stores them as instance variables.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Details:
        - Creates three Alarm objects with different descriptions and times.
        - Stores the created Alarm objects as instance variables (self.al1, self.al2, self.al3) for use in tests.
        - The Alarm model is assumed to have fields 'desc' (description) and 'time' (
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
        Tests the filtering of alarms based on the 'minute' attribute of their 'time' field.
        
        Parameters:
        self (TestInstance): The test instance, typically an instance of a unittest.TestCase subclass.
        
        Returns:
        None: This function asserts the equality of two sequences, so it does not return any value. It is used to verify the correctness of the query.
        
        Key Points:
        - The function uses `assertSequenceEqual` to check if the query result matches the expected output.
        - The
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
