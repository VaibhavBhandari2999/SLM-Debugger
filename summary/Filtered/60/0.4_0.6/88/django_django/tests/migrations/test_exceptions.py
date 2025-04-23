from django.db.migrations.exceptions import NodeNotFoundError
from django.test import SimpleTestCase


class ExceptionTests(SimpleTestCase):
    def test_node_not_found_error_repr(self):
        """
        Test the representation of a NodeNotFoundError.
        
        This function tests the string representation of the NodeNotFoundError exception.
        It takes a node tuple as input, which consists of an application label and a migration label.
        The function creates an instance of NodeNotFoundError with a custom message and the provided node.
        The expected representation of the exception is then compared to the actual output.
        
        :param node: A tuple containing the application label and migration label of the missing node.
        :type node: tuple
        :raises AssertionError: If the generated representation
        """

        node = ('some_app_label', 'some_migration_label')
        error_repr = repr(NodeNotFoundError('some message', node))
        self.assertEqual(
            error_repr,
            "NodeNotFoundError(('some_app_label', 'some_migration_label'))"
        )
