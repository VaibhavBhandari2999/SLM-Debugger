from django.test import TestCase

from .models import Parent


class MutuallyReferentialTests(TestCase):

    def test_mutually_referential(self):
        """
        Test the functionality of a mutually referential relationship in a database model.
        
        This test function checks the behavior of a Parent model that has a mutually referential relationship with its children. The test involves creating a Parent instance and several Child instances associated with it. It then sets one of the children as the 'bestchild' of the Parent and verifies that the assignment and deletion work as expected.
        
        Parameters:
        None
        
        Keywords:
        None
        
        Returns:
        None
        
        Details:
        1. A Parent
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
