from django.db import connection
from django.test import TestCase


class SchemaLoggerTests(TestCase):

    def test_extra_args(self):
        """
        Tests the execution of a SQL query with extra arguments using a schema editor.
        
        This function creates a schema editor instance and executes a SQL query with provided parameters. It captures the SQL query and its parameters and logs them for debugging purposes.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `sql` (str): The SQL query to be executed.
        - `params` (list): The parameters to be used in the SQL query.
        
        Logging:
        - Logs the SQL query
        """

        editor = connection.schema_editor(collect_sql=True)
        sql = 'SELECT * FROM foo WHERE id in (%s, %s)'
        params = [42, 1337]
        with self.assertLogs('django.db.backends.schema', 'DEBUG') as cm:
            editor.execute(sql, params)
        self.assertEqual(cm.records[0].sql, sql)
        self.assertEqual(cm.records[0].params, params)
        self.assertEqual(
            cm.records[0].getMessage(),
            'SELECT * FROM foo WHERE id in (%s, %s); (params [42, 1337])',
        )
