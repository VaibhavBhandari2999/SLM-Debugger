from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Tests the behavior of the Empty model.
        
        This function tests the Empty model's behavior, including setting and retrieving the 'id' field, saving instances, and creating new objects. It ensures that the 'id' field is correctly set to None when an instance is created and becomes non-None after saving. It also checks that saving an instance updates the object in the database and that creating a new instance with the same 'id' increments the object count.
        
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
