from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Test the behavior of the Empty model.
        
        This test function checks the creation and saving of an Empty model instance. It verifies that an instance without an ID is created correctly and that saving the instance assigns it an ID. Additionally, it ensures that creating another instance and saving it increases the count of objects in the database.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Create an instance of the Empty model without providing an ID.
        2. Assert that the instance's ID is initially
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
