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
        """
        Test the get_table_list method of the introspection class.
        
        This method is expected to raise a NotImplementedError with a specific message if the method is not implemented.
        
        Parameters:
        None
        
        Raises:
        NotImplementedError: If the method is not implemented, with a message indicating that the method is not implemented.
        
        Usage:
        This method should be used to verify that the get_table_list method is implemented correctly. If the method is not implemented, it should raise a NotImplementedError with the message: 'get_table_list()
        """

        msg = self.may_require_msg % 'get_table_list'
        with self.assertRaisesMessage(NotImplementedError, msg):
            self.introspection.get_table_list(None)

    def test_get_table_description(self):
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
        
        This method is expected to return the columns that define a key for a given table. If this method is not implemented, a NotImplementedError is raised with a specific message indicating that the method is not supported.
        
        Parameters:
        table_name (str): The name of the table for which to determine the key columns.
        
        Raises:
        NotImplementedError: If the get_key_columns method is not implemented.
        
        Note:
        This test checks whether the get_key_columns method is implemented and raises an
        """

        msg = self.may_require_msg % 'get_key_columns'
        with self.assertRaisesMessage(NotImplementedError, msg):
            self.introspection.get_key_columns(None, None)

    def test_get_constraints(self):
        msg = self.may_require_msg % 'get_constraints'
        with self.assertRaisesMessage(NotImplementedError, msg):
            self.introspection.get_constraints(None, None)
