from django.test import SimpleTestCase
from django.test.testcases import SerializeMixin


class TestSerializeMixin(SimpleTestCase):
    def test_init_without_lockfile(self):
        """
        Tests the `test_init_without_lockfile` method of the `SerializeMixin` class.
        
        This method checks if the `ExampleTests.lockfile` attribute is set. If it is not set, a `ValueError` is raised with a specific message indicating that the attribute should be set to a unique value in the base class.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If `ExampleTests.lockfile` is not set, a `ValueError` is raised with
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
