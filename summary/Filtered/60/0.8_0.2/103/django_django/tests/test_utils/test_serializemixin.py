from django.test import SimpleTestCase
from django.test.testcases import SerializeMixin


class TestSerializeMixin(SimpleTestCase):
    def test_init_without_lockfile(self):
        """
        Test the initialization of `SerializeMixin` without a lockfile.
        
        This test checks that `SerializeMixin` raises a `ValueError` when the `lockfile`
        attribute is not set. The `lockfile` attribute should be set to a unique value
        in the base class.
        
        Parameters:
        None
        
        Raises:
        ValueError: If `lockfile` is not set in the base class.
        
        Returns:
        None
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
