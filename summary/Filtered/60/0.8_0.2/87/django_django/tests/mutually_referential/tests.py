from django.test import TestCase

from .models import Parent


class MutuallyReferentialTests(TestCase):

    def test_mutually_referential(self):
        """
        Tests the functionality of a mutually referential relationship in a database model.
        
        This test function creates a Parent object and two Child objects associated with it. It then sets one of the children as the 'bestchild' of the parent and saves the changes. Finally, it deletes the parent object.
        
        Key Parameters:
        - None
        
        Keywords:
        - Parent: The parent object in the database.
        - Child: The child objects associated with the parent.
        - bestchild: The child object designated as the best child of
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
