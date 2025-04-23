from django.test import SimpleTestCase
from django.test.testcases import SerializeMixin


class TestSerializeMixin(SimpleTestCase):
    def test_init_without_lockfile(self):
        """
        Test initializing a test case without a lockfile.
        
        This function checks if the `ExampleTests.lockfile` attribute is set. If it is not set, a `ValueError` is raised with a specific message indicating that the lockfile should be set to a unique value in the base class. The function takes no parameters and does not return any value. It raises a `ValueError` if the lockfile is not set.
        """

        msg = (
            "ExampleTests.lockfile isn't set. Set it to a unique value in the "
            "base class."
        )
        with self.assertRaisesMessage(ValueError, msg):

            class ExampleTests(SerializeMixin, SimpleTestCase):
                pass


class TestSerializeMixinUse(SerializeMixin, SimpleTestCase):
    lockfile = __file__

    def test_usage(self):
        # Running this test ensures that the lock/unlock functions have passed.
        pass
