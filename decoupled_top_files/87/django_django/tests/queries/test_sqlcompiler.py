"""
```markdown
This Python script contains unit tests for Django's SQL query compilation process. It focuses on testing the `SQLCompiler` class used by Django's ORM to compile queries into SQL statements. Specifically, it tests the `repr` method of the `SQLCompiler` for a custom model `Item`.

#### Classes and Functions:
- **SQLCompilerTest**: A subclass of `SimpleTestCase` from Django's testing framework, designed to test the `SQLCompiler` functionality.
- **test_repr**: A test method within `SQLCompilerTest` that verifies the string representation of the `SQLCompiler` instance for a `Query` object associated with the `Item` model.

#### Key Responsibilities:
- The `test_repr` method ensures that the `
"""
from django.db import DEFAULT_DB_ALIAS, connection
from django.db.models.sql import Query
from django.test import SimpleTestCase

from .models import Item


class SQLCompilerTest(SimpleTestCase):
    def test_repr(self):
        """
        Tests the representation of an SQLCompiler instance for a Query object associated with the Item model. The function creates a Query object for the Item model, retrieves its SQLCompiler using the default database alias and the connection object, and asserts that the representation of the compiler matches the expected format, which includes the model name, database wrapper vendor, and alias.
        """

        query = Query(Item)
        compiler = query.get_compiler(DEFAULT_DB_ALIAS, connection)
        self.assertEqual(
            repr(compiler),
            f"<SQLCompiler model=Item connection="
            f"<DatabaseWrapper vendor={connection.vendor!r} alias='default'> "
            f"using='default'>"
        )
