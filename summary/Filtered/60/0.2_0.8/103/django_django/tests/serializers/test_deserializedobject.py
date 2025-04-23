from django.core.serializers.base import DeserializedObject
from django.test import SimpleTestCase

from .models import Author


class TestDeserializedObjectTests(SimpleTestCase):
    def test_repr(self):
        """
        Tests the `repr` method of the `DeserializedObject` class.
        
        This method checks if the `repr` output of a `DeserializedObject` instance is as expected. The `DeserializedObject` is initialized with an `Author` object having a name 'John' and primary key 1. The expected `repr` output is provided as a string, and the test asserts that the actual `repr` output matches this expected string.
        
        Parameters:
        None
        
        Returns:
        None
        """

        author = Author(name="John", pk=1)
        deserial_obj = DeserializedObject(obj=author)
        self.assertEqual(
            repr(deserial_obj), "<DeserializedObject: serializers.Author(pk=1)>"
        )
