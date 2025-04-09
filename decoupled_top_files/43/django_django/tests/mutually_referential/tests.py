from django.test import TestCase

from .models import Parent


class MutuallyReferentialTests(TestCase):

    def test_mutually_referential(self):
        """
        Tests the functionality of mutually referential relationships between Parent and Child models. Creates a Parent instance, adds two Child instances to its child_set, sets one Child as the bestchild, and deletes the Parent instance.
        
        Keywords: Parent, Child, child_set, bestchild, save, delete
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
