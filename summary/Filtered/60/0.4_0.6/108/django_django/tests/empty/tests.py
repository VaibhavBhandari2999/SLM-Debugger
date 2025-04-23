from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Function: test_empty
        Summary: Tests the behavior of the Empty model, which is a subclass of Django's Model class. This test ensures that an instance of Empty can be created, saved, and retrieved from the database.
        
        Parameters:
        - self: The test case instance (unittest.TestCase).
        
        Returns:
        - None: This function does not return any value. It performs assertions to validate the model's behavior.
        
        Key Points:
        - Creates an instance of the Empty model and checks if its 'id'
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
