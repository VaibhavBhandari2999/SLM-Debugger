from django.db.migrations.exceptions import NodeNotFoundError
from django.test import SimpleTestCase


class ExceptionTests(SimpleTestCase):
    def test_node_not_found_error_repr(self):
        """
        Tests the representation of the NodeNotFoundError exception.
        
        This function checks that the representation of the NodeNotFoundError exception
        correctly includes the provided message and the node for which the error was
        raised. The node is a tuple containing the application label and the migration
        label.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        >>> node = ('some_app_label', 'some_migration_label')
        >>> error_repr = repr(NodeNotFoundError('some message', node))
        >>> error_repr
        "
        """

        node = ('some_app_label', 'some_migration_label')
        error_repr = repr(NodeNotFoundError('some message', node))
        self.assertEqual(
            error_repr,
            "NodeNotFoundError(('some_app_label', 'some_migration_label'))"
        )
