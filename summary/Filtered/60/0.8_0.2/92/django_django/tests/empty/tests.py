from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Tests the behavior of the Empty model.
        
        This function tests the Empty model's behavior when instances are created and saved. It creates an instance of the Empty model, checks if its ID is initially None, saves the instance, and verifies that the ID is no longer None. It also checks that creating a new instance and saving it increases the count of objects in the database.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        m (Empty): An instance of the Empty model.
        Empty
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
