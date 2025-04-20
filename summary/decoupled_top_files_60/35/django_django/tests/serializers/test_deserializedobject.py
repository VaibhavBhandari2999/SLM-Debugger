from django.core.serializers.base import DeserializedObject
from django.test import SimpleTestCase

from .models import Author


class TestDeserializedObjectTests(SimpleTestCase):

    def test_repr(self):
        """
        Tests the `repr` method of the `DeserializedObject` class.
        
        Args:
        self: The instance of the test case.
        
        This method checks if the `repr` of a `DeserializedObject` instance correctly represents the object it contains. The object in this case is an `Author` instance with a name 'John' and primary key 1. The expected output is a string that indicates the class name and the primary key of the contained object.
        
        Returns:
        None
        """

        author = Author(name='John', pk=1)
        deserial_obj = DeserializedObject(obj=author)
        self.assertEqual(repr(deserial_obj), '<DeserializedObject: serializers.Author(pk=1)>')
