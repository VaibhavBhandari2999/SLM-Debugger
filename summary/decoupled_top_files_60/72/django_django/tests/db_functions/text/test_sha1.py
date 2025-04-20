from django.db import connection
from django.db.models import CharField
from django.db.models.functions import SHA1
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class SHA1Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Author model.
        
        This method creates a set of test data for the Author model using the `bulk_create` method. The test data includes five instances of the Author model with different alias values.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        """

        Author.objects.bulk_create([
            Author(alias='John Smith'),
            Author(alias='Jordan Élena'),
            Author(alias='皇帝'),
            Author(alias=''),
            Author(alias=None),
        ])

    def test_basic(self):
        """
        Tests the basic functionality of the Author model's SHA1 annotation.
        
        This test checks the output of the `Author` model when annotated with a SHA1 hash of the 'alias' field. The annotated field is then used to generate a list of unique SHA1 hashes for each author, ordered by primary key. The expected output is a sequence of SHA1 hashes, with potential null values if the database interprets empty strings as nulls.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        """

        authors = Author.objects.annotate(
            sha1_alias=SHA1('alias'),
        ).values_list('sha1_alias', flat=True).order_by('pk')
        self.assertSequenceEqual(
            authors,
            [
                'e61a3587b3f7a142b8c7b9263c82f8119398ecb7',
                '0781e0745a2503e6ded05ed5bc554c421d781b0c',
                '198d15ea139de04060caf95bc3e0ec5883cba881',
                'da39a3ee5e6b4b0d3255bfef95601890afd80709',
                'da39a3ee5e6b4b0d3255bfef95601890afd80709'
                if connection.features.interprets_empty_strings_as_nulls else None,
            ],
        )

    def test_transform(self):
        with register_lookup(CharField, SHA1):
            authors = Author.objects.filter(
                alias__sha1='e61a3587b3f7a142b8c7b9263c82f8119398ecb7',
            ).values_list('alias', flat=True)
            self.assertSequenceEqual(authors, ['John Smith'])
