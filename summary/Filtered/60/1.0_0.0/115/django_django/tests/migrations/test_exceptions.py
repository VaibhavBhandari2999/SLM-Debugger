from django.db.migrations.exceptions import NodeNotFoundError
from django.test import SimpleTestCase


class ExceptionTests(SimpleTestCase):
    def test_node_not_found_error_repr(self):
        """
        Test the representation of a NodeNotFoundError.
        
        This function tests the string representation of the NodeNotFoundError class. It takes a tuple representing a node (app label and migration label) and checks if the string representation of the exception matches the expected format.
        
        Parameters:
        node (tuple): A tuple containing the app label and migration label of the node that was not found.
        
        Returns:
        None: This function asserts that the string representation of the exception matches the expected format and does not return any value.
        
        Example:
        """

        node = ("some_app_label", "some_migration_label")
        error_repr = repr(NodeNotFoundError("some message", node))
        self.assertEqual(
            error_repr, "NodeNotFoundError(('some_app_label', 'some_migration_label'))"
        )
