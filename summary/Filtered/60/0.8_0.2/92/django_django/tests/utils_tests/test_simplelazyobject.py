import pickle

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.functional import SimpleLazyObject


class TestUtilsSimpleLazyObjectDjangoTestCase(TestCase):
    def test_pickle(self):
        """
        Tests the pickling of a SimpleLazyObject.
        
        This function creates a user object, wraps it in a SimpleLazyObject, and then attempts to pickle the object using different protocol levels. The function does not return any value but is expected to demonstrate that the SimpleLazyObject can be successfully pickled.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a user object using `User.objects.create_user`.
        - Wraps the user object in a `SimpleLazyObject`.
        - Attempts
        """

        user = User.objects.create_user("johndoe", "john@example.com", "pass")
        x = SimpleLazyObject(lambda: user)
        pickle.dumps(x)
        # Try the variant protocol levels.
        pickle.dumps(x, 0)
        pickle.dumps(x, 1)
        pickle.dumps(x, 2)
