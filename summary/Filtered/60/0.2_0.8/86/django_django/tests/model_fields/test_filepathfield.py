import os

from django.db.models import FilePathField
from django.test import SimpleTestCase


class FilePathFieldTests(SimpleTestCase):
    def test_path(self):
        """
        Tests the FilePathField by setting the path parameter and verifying that the field's path matches the provided value. The function creates an instance of FilePathField with the specified path and checks if the path attribute of the field matches the provided path. It also ensures that the formfield's path attribute is set correctly.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - path: The directory path to be set for the FilePathField.
        
        Usage:
        This function is used to validate the FilePath
        """

        path = os.path.dirname(__file__)
        field = FilePathField(path=path)
        self.assertEqual(field.path, path)
        self.assertEqual(field.formfield().path, path)

    def test_callable_path(self):
        path = os.path.dirname(__file__)

        def generate_path():
            return path

        field = FilePathField(path=generate_path)
        self.assertEqual(field.path(), path)
        self.assertEqual(field.formfield().path, path)
