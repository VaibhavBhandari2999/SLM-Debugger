from django.db import connection
from django.db.models import CharField
from django.db.models.functions import MD5
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class MD5Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Author model.
        
        This method creates and bulk inserts a set of Author objects into the database for testing purposes. The Author objects are initialized with various alias values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Example:
        This method is typically used in a Django test case setup to provide a consistent set of test data for subsequent tests.
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
        """
        Tests the basic functionality of the Author model's MD5 annotation.
        
        This test checks the MD5 hash of the 'alias' field for a list of authors. The MD5 hashes are annotated and then ordered by primary key. The expected MD5 hashes are compared against the actual results.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The sequence of MD5 hashes for the authors should match the expected sequence.
        """

        authors = (
            Author.objects.annotate(
                md5_alias=MD5("alias"),
            )
            .values_list("md5_alias", flat=True)
            .order_by("pk")
        )
        self.assertSequenceEqual(
            authors,
            [
                "6117323d2cabbc17d44c2b44587f682c",
                "ca6d48f6772000141e66591aee49d56c",
                "bf2c13bc1154e3d2e7df848cbc8be73d",
                "d41d8cd98f00b204e9800998ecf8427e",
                "d41d8cd98f00b204e9800998ecf8427e"
                if connection.features.interprets_empty_strings_as_nulls
                else None,
            ],
        )

    def test_transform(self):
        """
        Tests the transformation of a CharField using the MD5 lookup.
        
        This function registers a custom lookup for the CharField and filters the Author objects based on the MD5 hash of the alias field. It then retrieves the alias values that match the specified MD5 hash and asserts that the result is as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Assertions:
        """

        with register_lookup(CharField, MD5):
            authors = Author.objects.filter(
                alias__md5="6117323d2cabbc17d44c2b44587f682c",
            ).values_list("alias", flat=True)
            self.assertSequenceEqual(authors, ["John Smith"])
