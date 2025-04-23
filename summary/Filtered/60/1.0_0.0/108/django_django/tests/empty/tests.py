from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Tests the behavior of the Empty model.
        
        This function tests the Empty model by creating instances and checking their properties. It creates an instance of the Empty model, checks if its ID is initially None, saves the instance, and then checks if the ID is no longer None. It also creates another instance using the create method and verifies the count of objects in the database. Finally, it creates another instance with the ID from the first instance and saves it.
        
        Parameters:
        None
        
        Returns:
        None
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
