from django.db import DEFAULT_DB_ALIAS, connection
from django.db.models.sql import Query
from django.test import SimpleTestCase

from .models import Item


class SQLCompilerTest(SimpleTestCase):
    def test_repr(self):
        """
        Tests the representation of the SQLCompiler object for a Query instance. The function creates a Query object for the Item model, retrieves the SQLCompiler instance for the default database alias, and asserts that the string representation of the compiler matches the expected format. The expected format includes details about the model, the database connection, and the alias used.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Expected Output:
        - The function asserts that the string representation of the SQLCompiler matches the expected format, which includes details
        """

        query = Query(Item)
        compiler = query.get_compiler(DEFAULT_DB_ALIAS, connection)
        self.assertEqual(
            repr(compiler),
            f"<SQLCompiler model=Item connection="
            f"<DatabaseWrapper vendor={connection.vendor!r} alias='default'> "
            f"using='default'>"
        )
