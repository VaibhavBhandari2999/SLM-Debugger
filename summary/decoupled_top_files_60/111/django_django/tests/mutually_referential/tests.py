from django.test import TestCase

from .models import Parent


class MutuallyReferentialTests(TestCase):
    def test_mutually_referential(self):
        """
        Tests the functionality of a mutually referential relationship in a database model.
        
        This test checks the ability of a Parent model to set and save a reference to one of its children as the 'bestchild'. It also tests the deletion of the Parent and its associated children.
        
        Key Parameters:
        - `self`: The test case instance (unittest.TestCase).
        
        Key Steps:
        1. Creates a `Parent` instance named "Elizabeth".
        2. Saves the `Parent` instance to the database.
        3. Creates two `
        """

        # Create a Parent
        q = Parent(name="Elizabeth")
        q.save()

        # Create some children
        c = q.child_set.create(name="Charles")
        q.child_set.create(name="Edward")

        # Set the best child
        # No assertion require here; if basic assignment and
        # deletion works, the test passes.
        q.bestchild = c
        q.save()
        q.delete()
