from django.db.migrations.exceptions import NodeNotFoundError
from django.test import SimpleTestCase


class ExceptionTests(SimpleTestCase):
    def test_node_not_found_error_repr(self):
        """
        Tests the representation of a NodeNotFoundError when a specified migration node is not found.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        None
        
        Summary:
        This function tests the string representation of a NodeNotFoundError exception, which is raised when a specific migration node is not found. The function takes a tuple representing the migration node (app label, migration label) and generates the expected representation of the exception. The generated representation is then compared with the expected value using an assertion
        """

        node = ('some_app_label', 'some_migration_label')
        error_repr = repr(NodeNotFoundError('some message', node))
        self.assertEqual(
            error_repr,
            "NodeNotFoundError(('some_app_label', 'some_migration_label'))"
        )
