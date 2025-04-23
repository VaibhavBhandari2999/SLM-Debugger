from django.db import connection
from django.db.models import CharField
from django.db.models.functions import SHA256
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class SHA256Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Author model.
        
        This method creates and bulk inserts a set of predefined Author instances into the database for testing purposes. The Author instances are created with various alias values, including strings with different characters and empty or null values.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Example Usage:
        ```python
        class AuthorModelTest(TestCase):
        @classmethod
        def setUpTestData(cls):
        # Setup test data for the Author model
        Author.objects.bulk_create([
        Author
        """

        Author.objects.bulk_create(
            [
                Author(alias="John Smith"),
                Author(alias="Jordan Élena"),
                Author(alias="皇帝"),
                Author(alias=""),
                Author(alias=None),
            ]
        )

    def test_basic(self):
        authors = (
            Author.objects.annotate(
                sha256_alias=SHA256("alias"),
            )
            .values_list("sha256_alias", flat=True)
            .order_by("pk")
        )
        self.assertSequenceEqual(
            authors,
            [
                "ef61a579c907bbed674c0dbcbcf7f7af8f851538eef7b8e58c5bee0b8cfdac4a",
                "6e4cce20cd83fc7c202f21a8b2452a68509cf24d1c272a045b5e0cfc43f0d94e",
                "3ad2039e3ec0c88973ae1c0fce5a3dbafdd5a1627da0a92312c54ebfcf43988e",
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                if connection.features.interprets_empty_strings_as_nulls
                else None,
            ],
        )

    def test_transform(self):
        """
        Tests the transformation of a CharField using the SHA256 lookup.
        
        This test registers a custom lookup for the CharField and filters the Author objects based on a SHA256 hash of the alias field. The expected output is a list of aliases that match the given hash.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Registers a custom lookup `SHA256` for the `CharField`.
        - Filters `Author` objects where the SHA25
        """

        with register_lookup(CharField, SHA256):
            authors = Author.objects.filter(
                alias__sha256=(
                    "ef61a579c907bbed674c0dbcbcf7f7af8f851538eef7b8e58c5bee0b8cfdac4a"
                ),
            ).values_list("alias", flat=True)
            self.assertSequenceEqual(authors, ["John Smith"])
