from django.test import TestCase

from .models import Parent


class MutuallyReferentialTests(TestCase):
    def test_mutually_referential(self):
        """
        Tests the functionality of mutually referential relationships between Parent and Child models. Creates a Parent instance named 'Elizabeth', adds two Child instances named 'Charles' and 'Edward', sets one of the children as the 'bestchild', and then deletes the Parent instance. This tests the assignment and deletion operations in a mutually referential relationship.
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
