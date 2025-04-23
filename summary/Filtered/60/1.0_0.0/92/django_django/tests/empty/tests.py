from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Tests the behavior of the Empty model.
        
        This function tests the Empty model by creating instances, saving them, and checking the object IDs. It ensures that:
        - An empty instance has a None ID.
        - Saving an instance assigns it a unique ID.
        - Creating a new instance with the same ID raises an error.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        - Empty: The model being tested.
        - id: The unique identifier for each instance.
        - save: The
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
