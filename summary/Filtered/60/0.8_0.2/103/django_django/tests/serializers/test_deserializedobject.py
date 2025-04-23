from django.core.serializers.base import DeserializedObject
from django.test import SimpleTestCase

from .models import Author


class TestDeserializedObjectTests(SimpleTestCase):
    def test_repr(self):
        """
        Test the representation of a DeserializedObject.
        
        This test checks that the `repr` of a DeserializedObject correctly displays the object type and primary key of the serialized object.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Details:
        - `author`: An instance of the `Author` class with a name and primary key.
        - `deserial_obj`: An instance of `DeserializedObject` containing the serialized `author` object.
        - The expected `repr` output is
        """

        author = Author(name="John", pk=1)
        deserial_obj = DeserializedObject(obj=author)
        self.assertEqual(
            repr(deserial_obj), "<DeserializedObject: serializers.Author(pk=1)>"
        )
