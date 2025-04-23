from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Test the behavior of the Empty model.
        
        This test function checks the creation and saving of an Empty model instance. It verifies that an instance without an ID is created correctly and that saving it assigns an ID. Additionally, it ensures that creating another instance through the ORM adds it to the database and that saving an existing instance updates its state.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Verifications:
        - An instance of Empty without an ID is created and has a None ID.
        -
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
