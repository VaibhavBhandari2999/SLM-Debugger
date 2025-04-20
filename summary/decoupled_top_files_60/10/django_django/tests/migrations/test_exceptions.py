from django.db.migrations.exceptions import NodeNotFoundError
from django.test import SimpleTestCase


class ExceptionTests(SimpleTestCase):
    def test_node_not_found_error_repr(self):
        """
        Tests the representation of a NodeNotFoundError exception.
        
        This function checks that the representation of a NodeNotFoundError exception
        correctly includes the app label and migration label of the missing node.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        >>> node = ('some_app_label', 'some_migration_label')
        >>> error_repr = repr(NodeNotFoundError('some message', node))
        >>> error_repr
        "NodeNotFoundError(('some_app_label', 'some_migration_label'))"
        """

        node = ('some_app_label', 'some_migration_label')
        error_repr = repr(NodeNotFoundError('some message', node))
        self.assertEqual(
            error_repr,
            "NodeNotFoundError(('some_app_label', 'some_migration_label'))"
        )
