from django.test import TestCase

from .models import Parent


class MutuallyReferentialTests(TestCase):
    def test_mutually_referential(self):
        """
        Test the functionality of a mutually referential relationship in a database model.
        
        This test function creates a `Parent` instance and two `Child` instances associated with it. It then sets one of the children as the `bestchild` of the parent and saves the changes. Finally, it deletes the parent instance.
        
        Key Parameters:
        - `self`: The test case instance.
        
        Input:
        - No external inputs are required. The test internally creates instances of `Parent` and `Child`.
        
        Output:
        - No
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
