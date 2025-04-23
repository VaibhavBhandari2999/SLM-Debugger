from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Tests the behavior of the Empty model.
        
        This function tests the Empty model's behavior, including the creation of instances, saving, and querying the database. It checks that an instance with no ID is created correctly, that saving an instance assigns it an ID, and that creating another instance increments the object count.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        - m: An instance of the Empty model.
        - Empty: The model class being tested.
        - Empty.objects: The
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
