from django.test import TestCase

from .models import Parent


class MutuallyReferentialTests(TestCase):

    def test_mutually_referential(self):
        """
        Test the functionality of a mutually referential relationship in a database model.
        
        This test function checks the behavior of a parent-child relationship where the parent and child models reference each other. The test involves creating a parent object and multiple child objects, setting one of the children as the parent's best child, and then deleting the parent object. The test ensures that the assignment and deletion operations work as expected.
        
        Key Parameters:
        - None (The test uses objects created within the function)
        
        Keywords:
        - Parent: The
        """

        # Create a Parent
        q = Parent(name='Elizabeth')
        q.save()

        # Create some children
        c = q.child_set.create(name='Charles')
        q.child_set.create(name='Edward')

        # Set the best child
        # No assertion require here; if basic assignment and
        # deletion works, the test passes.
        q.bestchild = c
        q.save()
        q.delete()
