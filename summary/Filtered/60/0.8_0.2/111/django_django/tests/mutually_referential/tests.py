from django.test import TestCase

from .models import Parent


class MutuallyReferentialTests(TestCase):
    def test_mutually_referential(self):
        """
        Test the functionality of a mutually referential relationship in a database model.
        
        This test function checks the behavior of a parent-child relationship where both the parent and child models reference each other. The test involves creating a parent instance and multiple child instances, setting one child as the 'bestchild', and then deleting the parent. The test ensures that the assignment and deletion operations work as expected.
        
        Key Parameters:
        - None (The test uses instance variables and does not take any parameters).
        
        Keywords:
        - Parent: A
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
