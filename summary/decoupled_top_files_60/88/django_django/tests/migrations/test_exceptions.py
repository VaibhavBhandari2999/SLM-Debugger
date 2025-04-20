from django.db.migrations.exceptions import NodeNotFoundError
from django.test import SimpleTestCase


class ExceptionTests(SimpleTestCase):
    def test_node_not_found_error_repr(self):
        """
        Tests the `NodeNotFoundError` exception representation.
        
        This function checks that the `NodeNotFoundError` exception is correctly represented when a node is not found. The exception is initialized with a message and a node tuple, which consists of an application label and a migration label. The function asserts that the representation of the exception matches the expected string.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the representation of the `NodeNotFoundError` exception does not match the expected string.
        
        Example:
        """

        node = ('some_app_label', 'some_migration_label')
        error_repr = repr(NodeNotFoundError('some message', node))
        self.assertEqual(
            error_repr,
            "NodeNotFoundError(('some_app_label', 'some_migration_label'))"
        )
