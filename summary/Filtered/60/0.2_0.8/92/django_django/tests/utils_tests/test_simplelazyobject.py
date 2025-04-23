import pickle

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.functional import SimpleLazyObject


class TestUtilsSimpleLazyObjectDjangoTestCase(TestCase):
    def test_pickle(self):
        """
        Tests the pickling of a SimpleLazyObject.
        
        This function creates a user object, wraps it in a SimpleLazyObject, and then attempts to pickle the object using the standard pickling protocol. It also tests the pickling process with different protocol levels (0, 1, and 2).
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A user is created using `User.objects.create_user`.
        - The user is wrapped in a `SimpleLazyObject`.
        - The object
        """

        user = User.objects.create_user("johndoe", "john@example.com", "pass")
        x = SimpleLazyObject(lambda: user)
        pickle.dumps(x)
        # Try the variant protocol levels.
        pickle.dumps(x, 0)
        pickle.dumps(x, 1)
        pickle.dumps(x, 2)
