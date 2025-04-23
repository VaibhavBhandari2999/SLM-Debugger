import os

from django.db.models import FilePathField
from django.test import SimpleTestCase


class FilePathFieldTests(SimpleTestCase):
    def test_path(self):
        path = os.path.dirname(__file__)
        field = FilePathField(path=path)
        self.assertEqual(field.path, path)
        self.assertEqual(field.formfield().path, path)

    def test_callable_path(self):
        """
        Tests the FilePathField with a callable path.
        
        This function checks the behavior of the FilePathField when the path is provided by a callable function. The callable function `generate_path` returns the directory path of the current file. The test verifies that the FilePathField correctly uses the path returned by the callable and that the formfield retains the correct path.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Verifications:
        - The FilePathField correctly uses the path returned by the callable function.
        -
        """

        path = os.path.dirname(__file__)

        def generate_path():
            return path

        field = FilePathField(path=generate_path)
        self.assertEqual(field.path(), path)
        self.assertEqual(field.formfield().path, path)
