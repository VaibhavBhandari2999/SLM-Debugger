from django.test import TestCase

from .models import Empty


class EmptyModelTests(TestCase):
    def test_empty(self):
        """
        Tests the behavior of the Empty model.
        
        This function tests the Empty model by creating instances and checking their properties. It creates an instance of the Empty model, verifies that its 'id' is initially None, saves the instance, and then checks that the 'id' is no longer None. It also creates another instance using the create method and ensures that the total count of instances in the database is 2. Finally, it creates another instance using the 'id' of the first instance and saves it
        """

        m = Empty()
        self.assertIsNone(m.id)
        m.save()
        Empty.objects.create()
        self.assertEqual(len(Empty.objects.all()), 2)
        self.assertIsNotNone(m.id)
        existing = Empty(m.id)
        existing.save()
