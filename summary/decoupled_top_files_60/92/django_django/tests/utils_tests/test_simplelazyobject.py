import pickle

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.functional import SimpleLazyObject


class TestUtilsSimpleLazyObjectDjangoTestCase(TestCase):
    def test_pickle(self):
        """
        Tests the pickling functionality for a SimpleLazyObject.
        
        This function creates a user object and wraps it in a SimpleLazyObject. It then attempts to pickle the wrapped object using the standard pickling protocol and the variant protocol levels 0, 1, and 2.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a user object using `User.objects.create_user`.
        - Wraps the user object in a `SimpleLazyObject`.
        - Uses `pickle.dumps` to
        """

        user = User.objects.create_user("johndoe", "john@example.com", "pass")
        x = SimpleLazyObject(lambda: user)
        pickle.dumps(x)
        # Try the variant protocol levels.
        pickle.dumps(x, 0)
        pickle.dumps(x, 1)
        pickle.dumps(x, 2)
