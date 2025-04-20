from django.db import DEFAULT_DB_ALIAS, connection
from django.db.models.sql import Query
from django.test import SimpleTestCase

from .models import Item


class SQLCompilerTest(SimpleTestCase):
    def test_repr(self):
        """
        Tests the representation of a SQLCompiler object for a Query instance.
        
        This function checks the string representation of a SQLCompiler object that is created from a Query instance for the Item model. The representation includes details about the model and the database connection being used.
        
        Parameters:
        self: The instance of the test case class.
        
        Returns:
        None: This function asserts the expected representation against the actual representation of the SQLCompiler object, raising an AssertionError if they do not match.
        """

        query = Query(Item)
        compiler = query.get_compiler(DEFAULT_DB_ALIAS, connection)
        self.assertEqual(
            repr(compiler),
            f"<SQLCompiler model=Item connection="
            f"<DatabaseWrapper vendor={connection.vendor!r} alias='default'> "
            f"using='default'>",
        )
