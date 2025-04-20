from django.db import DEFAULT_DB_ALIAS, connection
from django.db.models.sql import Query
from django.test import SimpleTestCase

from .models import Item


class SQLCompilerTest(SimpleTestCase):
    def test_repr(self):
        """
        Tests the representation of a SQLCompiler object for a Query instance. The function creates a Query object for the Item model and retrieves its SQLCompiler using the default database alias and connection. The expected representation of the SQLCompiler is compared against the actual representation.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Expected Output:
        - The function asserts that the representation of the SQLCompiler matches the expected string:
        "<SQLCompiler model=Item connection=<DatabaseWrapper vendor=<connection.vendor!r> alias='default
        """

        query = Query(Item)
        compiler = query.get_compiler(DEFAULT_DB_ALIAS, connection)
        self.assertEqual(
            repr(compiler),
            f"<SQLCompiler model=Item connection="
            f"<DatabaseWrapper vendor={connection.vendor!r} alias='default'> "
            f"using='default'>"
        )
