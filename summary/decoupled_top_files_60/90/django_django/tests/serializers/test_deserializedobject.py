from django.core.serializers.base import DeserializedObject
from django.test import SimpleTestCase

from .models import Author


class TestDeserializedObjectTests(SimpleTestCase):

    def test_repr(self):
        """
        Tests the `repr` method of the `DeserializedObject` class.
        
        This method checks if the `repr` of a `DeserializedObject` instance correctly represents the serialized object's class name and primary key.
        
        Parameters:
        self: The test case instance.
        
        Returns:
        None: This method asserts the expected output and does not return any value.
        """

        author = Author(name='John', pk=1)
        deserial_obj = DeserializedObject(obj=author)
        self.assertEqual(repr(deserial_obj), '<DeserializedObject: serializers.Author(pk=1)>')
