from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Test the behavior of the Empty model.
        
        This test function checks the following:
        - An instance of the Empty model with no id is created and its id is None.
        - After saving the instance, it should have a valid id.
        - Creating another instance of the Empty model using the create method increases the count of objects in the database.
        - Saving an instance of the Empty model with a specific id updates the database.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        Empty model, instance
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
