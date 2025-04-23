from django.core.serializers.base import DeserializedObject
from django.test import SimpleTestCase

from .models import Author


class TestDeserializedObjectTests(SimpleTestCase):

    def test_repr(self):
        """
        Tests the `repr` method of the `DeserializedObject` class.
        
        Args:
        self: The instance of the test class.
        
        This method creates an instance of the `Author` class with a name 'John' and primary key 1. It then creates a `DeserializedObject` instance with this `Author` object. The `repr` method of the `DeserializedObject` instance is expected to return a string representation indicating the type of the object and its primary key, formatted as
        """

        author = Author(name='John', pk=1)
        deserial_obj = DeserializedObject(obj=author)
        self.assertEqual(repr(deserial_obj), '<DeserializedObject: serializers.Author(pk=1)>')
