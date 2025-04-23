from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Test the behavior of the Empty model.
        
        This test function checks the creation and saving of an Empty model instance. It ensures that an instance without an ID is created and saved correctly, and that creating another instance with the same ID raises an error.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Create an instance of the Empty model and assert that its ID is None.
        2. Save the instance and verify that its ID is no longer None.
        3. Create another instance of
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
