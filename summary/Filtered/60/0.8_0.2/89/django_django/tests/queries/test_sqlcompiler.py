from django.db import DEFAULT_DB_ALIAS, connection
from django.db.models.sql import Query
from django.test import SimpleTestCase

from .models import Item


class SQLCompilerTest(SimpleTestCase):
    def test_repr(self):
        """
        Tests the representation of a SQLCompiler object for a Query instance.
        
        This function checks the string representation of a SQLCompiler object that is generated for a Query instance targeting the Item model. The SQLCompiler is created using the default database alias and the connection object. The expected representation is a string that includes details about the model, the connection, and the alias used.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Example Output:
        - <SQLCompiler model=Item connection=<DatabaseWrapper vendor='sqlite'
        """

        query = Query(Item)
        compiler = query.get_compiler(DEFAULT_DB_ALIAS, connection)
        self.assertEqual(
            repr(compiler),
            f"<SQLCompiler model=Item connection="
            f"<DatabaseWrapper vendor={connection.vendor!r} alias='default'> "
            f"using='default'>"
        )
