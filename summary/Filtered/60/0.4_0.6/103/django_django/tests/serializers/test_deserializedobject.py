from django.core.serializers.base import DeserializedObject
from django.test import SimpleTestCase

from .models import Author


class TestDeserializedObjectTests(SimpleTestCase):
    def test_repr(self):
        """
        Tests the `repr` method of the `DeserializedObject` class.
        
        This test ensures that the `repr` method of the `DeserializedObject` class correctly returns a string representation of the object. Specifically, it checks that the representation includes the class name and the primary key (pk) of the object being serialized.
        
        Parameters:
        self: The test case instance.
        
        Inputs:
        - `author`: An instance of the `Author` class with name "John" and primary key 1
        """

        author = Author(name="John", pk=1)
        deserial_obj = DeserializedObject(obj=author)
        self.assertEqual(
            repr(deserial_obj), "<DeserializedObject: serializers.Author(pk=1)>"
        )
