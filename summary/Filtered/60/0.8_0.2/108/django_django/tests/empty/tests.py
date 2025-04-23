from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Test the behavior of the Empty model.
        
        This test function checks the following:
        - An instance of the Empty model with no data (i.e., `id` is `None`) is created.
        - After saving the instance, the `id` is no longer `None`.
        - Creating another instance of the Empty model using `objects.create()` increases the count of objects in the database to 2.
        - The `id` of the saved instance is used to retrieve and save another instance of the Empty
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
