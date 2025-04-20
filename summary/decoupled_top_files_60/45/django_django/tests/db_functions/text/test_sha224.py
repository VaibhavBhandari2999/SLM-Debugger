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
        
        This method creates and saves multiple instances of the Author model for use in testing. The data includes various aliases to test different scenarios.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Example Usage:
        ```python
        class AuthorModelTest(TestCase):
        @classmethod
        def setUpTestData(cls):
        Author.objects.bulk_create([
        Author(alias='John Smith'),
        Author(alias='Jordan Élena'),
        Author(alias='皇帝'),
        Author(alias=''),
        """

        Author.objects.bulk_create([
            Author(alias='John Smith'),
            Author(alias='Jordan Élena'),
            Author(alias='皇帝'),
            Author(alias=''),
            Author(alias=None),
        ])

    @unittest.skipIf(connection.vendor == 'oracle', "Oracle doesn't support SHA224.")
    def test_basic(self):
        authors = Author.objects.annotate(
            sha224_alias=SHA224('alias'),
        ).values_list('sha224_alias', flat=True).order_by('pk')
        self.assertSequenceEqual(
            authors,
            [
                'a61303c220731168452cb6acf3759438b1523e768f464e3704e12f70',
                '2297904883e78183cb118fc3dc21a610d60daada7b6ebdbc85139f4d',
                'eba942746e5855121d9d8f79e27dfdebed81adc85b6bf41591203080',
                'd14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f',
                'd14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f'
                if connection.features.interprets_empty_strings_as_nulls else None,
            ],
        )

    @unittest.skipIf(connection.vendor == 'oracle', "Oracle doesn't support SHA224.")
    def test_transform(self):
        """
        Tests the transformation of a CharField using the SHA224 lookup.
        
        This function registers a custom lookup for CharField and filters the Author objects based on the SHA224 hash of the alias field. The expected output is a list of aliases that match the given SHA224 hash.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Registers the SHA224 lookup for CharField.
        2. Filters Author objects where the SHA224 hash of the
        """

        with register_lookup(CharField, SHA224):
            authors = Author.objects.filter(
                alias__sha224='a61303c220731168452cb6acf3759438b1523e768f464e3704e12f70',
            ).values_list('alias', flat=True)
            self.assertSequenceEqual(authors, ['John Smith'])

    @unittest.skipUnless(connection.vendor == 'oracle', "Oracle doesn't support SHA224.")
    def test_unsupported(self):
        """
        Tests the behavior of the function when an unsupported hash function (SHA224) is attempted to be used with Oracle database backend.
        
        This function asserts that an NotSupportedError is raised with a specific error message when trying to use the SHA224 hash function on Oracle.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        NotSupportedError: If the SHA224 function is used on Oracle, an exception is raised with the message 'SHA224 is not supported
        """

        msg = 'SHA224 is not supported on Oracle.'
        with self.assertRaisesMessage(NotSupportedError, msg):
            Author.objects.annotate(sha224_alias=SHA224('alias')).first()
