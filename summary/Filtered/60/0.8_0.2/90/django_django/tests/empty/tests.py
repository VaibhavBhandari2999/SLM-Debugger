from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Test the behavior of the Empty model.
        
        This test function checks the following:
        - An instance of the Empty model with no ID is created and its ID is None.
        - After saving the instance, it gets an ID.
        - A second instance of the Empty model is created using the create method and added to the database.
        - The total number of instances in the database is 2 after these operations.
        - An existing instance is fetched by its ID and saved again.
        
        Parameters:
        - None
        
        Returns:
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
