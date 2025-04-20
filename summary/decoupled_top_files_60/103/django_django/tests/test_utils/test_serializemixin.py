from django.test import SimpleTestCase
from django.test.testcases import SerializeMixin


class TestSerializeMixin(SimpleTestCase):
    def test_init_without_lockfile(self):
        """
        Test the initialization of SerializeMixin without setting the lockfile attribute.
        
        This test checks that attempting to initialize a test class derived from SerializeMixin and SimpleTestCase without setting the lockfile attribute raises a ValueError with a specific message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the lockfile attribute is not set in the base class.
        
        Example:
        The following code will raise a ValueError:
        ```python
        class ExampleTests(SerializeMixin, SimpleTestCase):
        pass
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
