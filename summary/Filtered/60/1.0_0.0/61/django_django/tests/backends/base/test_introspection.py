from django.db import connection
from django.db.backends.base.introspection import BaseDatabaseIntrospection
from django.test import SimpleTestCase


class SimpleDatabaseIntrospectionTests(SimpleTestCase):
    may_require_msg = (
        'subclasses of BaseDatabaseIntrospection may require a %s() method'
    )

    def setUp(self):
        self.introspection = BaseDatabaseIntrospection(connection=connection)

    def test_get_table_list(self):
        msg = self.may_require_msg % 'get_table_list'
        with self.assertRaisesMessage(NotImplementedError, msg):
            self.introspection.get_table_list(None)

    def test_get_table_description(self):
        """
        Test the get_table_description method.
        
        This method is expected to raise a NotImplementedError with a specific message
        indicating that the method is not implemented. The message includes a placeholder
        for the method name.
        
        Parameters:
        None
        
        Raises:
        NotImplementedError: Always raised with a message indicating that the method
        is not implemented.
        
        Usage:
        This test case should be used to verify that the get_table_description method
        in the introspection class raises the expected exception with the correct message.
        """

        msg = self.may_require_msg % 'get_table_description'
        with self.assertRaisesMessage(NotImplementedError, msg):
            self.introspection.get_table_description(None, None)

    def test_get_sequences(self):
        msg = self.may_require_msg % 'get_sequences'
        with self.assertRaisesMessage(NotImplementedError, msg):
            self.introspection.get_sequences(None, None)

    def test_get_relations(self):
        msg = self.may_require_msg % 'get_relations'
        with self.assertRaisesMessage(NotImplementedError, msg):
            self.introspection.get_relations(None, None)

    def test_get_key_columns(self):
        """
        Test the get_key_columns method.
        
        This method is expected to return the key columns for a given table. If the method is not implemented, a NotImplementedError is raised with a specific message.
        
        Parameters:
        table_name (str): The name of the table for which to get the key columns.
        
        Raises:
        NotImplementedError: If the get_key_columns method is not implemented.
        Message: The message includes a reference to the method that needs to be implemented ('get_key_columns').
        
        Example:
        >>> intros
        """

        msg = self.may_require_msg % 'get_key_columns'
        with self.assertRaisesMessage(NotImplementedError, msg):
            self.introspection.get_key_columns(None, None)

    def test_get_constraints(self):
        msg = self.may_require_msg % 'get_constraints'
        with self.assertRaisesMessage(NotImplementedError, msg):
            self.introspection.get_constraints(None, None)
trospection.get_constraints(None, None)
