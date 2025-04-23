import os

from django.db.models import FilePathField
from django.test import SimpleTestCase


class FilePathFieldTests(SimpleTestCase):
    def test_path(self):
        """
        Test the FilePathField with a specified path.
        
        This function tests the behavior of the FilePathField by setting a specific path and verifying that the field correctly retains and returns this path.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Behavior:
        - Sets the path for the FilePathField.
        - Verifies that the field correctly stores the specified path.
        - Ensures that the formfield associated with the FilePathField also retains the specified path.
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
