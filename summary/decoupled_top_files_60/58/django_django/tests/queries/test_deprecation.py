from contextlib import contextmanager

from django.core.exceptions import FieldDoesNotExist, FieldError
from django.db.models.query_utils import InvalidQuery
from django.test import SimpleTestCase
from django.utils.deprecation import RemovedInDjango40Warning


class InvalidQueryTests(SimpleTestCase):
    @contextmanager
    def assert_warns(self):
        """
        Asserts that a warning is raised.
        
        This function is designed to test that a specific warning is raised when
        calling a certain piece of code. The warning is expected to be a
        RemovedInDjango40Warning with a specific message indicating that the
        InvalidQuery exception class is deprecated and should be replaced with
        FieldDoesNotExist or FieldError.
        
        Parameters:
        None
        
        Yields:
        None
        
        Raises:
        RemovedInDjango40Warning: If the warning is not raised with
        """

        msg = (
            'The InvalidQuery exception class is deprecated. Use '
            'FieldDoesNotExist or FieldError instead.'
        )
        with self.assertWarnsMessage(RemovedInDjango40Warning, msg):
            yield

    def test_type(self):
        self.assertIsInstance(InvalidQuery(), InvalidQuery)

    def test_isinstance(self):
        for exception in (FieldError, FieldDoesNotExist):
            with self.assert_warns(), self.subTest(exception.__name__):
                self.assertIsInstance(exception(), InvalidQuery)

    def test_issubclass(self):
        for exception in (FieldError, FieldDoesNotExist, InvalidQuery):
            with self.assert_warns(), self.subTest(exception.__name__):
                self.assertIs(issubclass(exception, InvalidQuery), True)
lass(exception, InvalidQuery), True)
