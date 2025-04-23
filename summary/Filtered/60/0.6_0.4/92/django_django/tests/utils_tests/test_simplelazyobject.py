import pickle

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.functional import SimpleLazyObject


class TestUtilsSimpleLazyObjectDjangoTestCase(TestCase):
    def test_pickle(self):
        """
        Tests the pickling of a SimpleLazyObject containing a Django User instance.
        
        This function creates a Django User instance and wraps it in a SimpleLazyObject. It then attempts to pickle the object using the standard pickling mechanism and also tests the pickling with different protocol levels (0, 1, and 2).
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a Django User instance with username 'johndoe', email 'john@example.com', and password '
        """

        user = User.objects.create_user("johndoe", "john@example.com", "pass")
        x = SimpleLazyObject(lambda: user)
        pickle.dumps(x)
        # Try the variant protocol levels.
        pickle.dumps(x, 0)
        pickle.dumps(x, 1)
        pickle.dumps(x, 2)
