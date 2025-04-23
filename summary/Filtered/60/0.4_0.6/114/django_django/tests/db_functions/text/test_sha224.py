import unittest

from django.db import NotSupportedError, connection
from django.db.models import CharField
from django.db.models.functions import SHA224
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class SHA224Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Author model.
        
        This method creates and saves multiple instances of the Author model in the database using bulk creation. The instances are initialized with different alias values, including strings with special characters, an empty string, and a null value.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Example Usage:
        ```python
        class AuthorModelTest(TestCase):
        @classmethod
        def setUpTestData(cls):
        # Call the method to set up test data
        cls.setUpTestData()
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
                sha224_alias=SHA224("alias"),
            )
            .values_list("sha224_alias", flat=True)
            .order_by("pk")
        )
        self.assertSequenceEqual(
            authors,
            [
                "a61303c220731168452cb6acf3759438b1523e768f464e3704e12f70",
                "2297904883e78183cb118fc3dc21a610d60daada7b6ebdbc85139f4d",
                "eba942746e5855121d9d8f79e27dfdebed81adc85b6bf41591203080",
                "d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f",
                "d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f"
                if connection.features.interprets_empty_strings_as_nulls
                else None,
            ],
        )

    def test_transform(self):
        with register_lookup(CharField, SHA224):
            authors = Author.objects.filter(
                alias__sha224=(
                    "a61303c220731168452cb6acf3759438b1523e768f464e3704e12f70"
                ),
            ).values_list("alias", flat=True)
            self.assertSequenceEqual(authors, ["John Smith"])

    @unittest.skipUnless(
        connection.vendor == "oracle", "Oracle doesn't support SHA224."
    )
    def test_unsupported(self):
        """
        Tests the behavior of an unsupported hashing function (SHA224) on Oracle databases.
        
        This function attempts to use the SHA224 hashing function on a database field named 'alias' from the 'Author' model. Since SHA224 is not supported on Oracle databases, this operation is expected to raise a NotSupportedError. The error message should match the expected message: "SHA224 is not supported on Oracle."
        
        Key Parameters:
        None
        
        Returns:
        None
        
        Raises
        """

        msg = "SHA224 is not supported on Oracle."
        with self.assertRaisesMessage(NotSupportedError, msg):
            Author.objects.annotate(sha224_alias=SHA224("alias")).first()
   Author.objects.annotate(sha224_alias=SHA224("alias")).first()
