from django.db import connection
from django.db.models import CharField
from django.db.models.functions import MD5
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class MD5Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.bulk_create([
            Author(alias='John Smith'),
            Author(alias='Jordan Élena'),
            Author(alias='皇帝'),
            Author(alias=''),
            Author(alias=None),
        ])

    def test_basic(self):
        authors = Author.objects.annotate(
            md5_alias=MD5('alias'),
        ).values_list('md5_alias', flat=True).order_by('pk')
        self.assertSequenceEqual(
            authors,
            [
                '6117323d2cabbc17d44c2b44587f682c',
                'ca6d48f6772000141e66591aee49d56c',
                'bf2c13bc1154e3d2e7df848cbc8be73d',
                'd41d8cd98f00b204e9800998ecf8427e',
                'd41d8cd98f00b204e9800998ecf8427e' if connection.features.interprets_empty_strings_as_nulls else None,
            ],
        )

    def test_transform(self):
        """
        Tests the transformation functionality for the CharField using the MD5 lookup.
        
        This function registers a custom lookup 'md5' for the CharField and then filters the Author objects based on the MD5 hash of the 'alias' field. The expected output is a queryset containing the aliases that match the specified MD5 hash.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        - register_lookup: Registers the custom MD5 lookup for CharField.
        - Author.objects.filter: Filters the Author
        """

        with register_lookup(CharField, MD5):
            authors = Author.objects.filter(
                alias__md5='6117323d2cabbc17d44c2b44587f682c',
            ).values_list('alias', flat=True)
            self.assertSequenceEqual(authors, ['John Smith'])
t=True)
            self.assertSequenceEqual(authors, ['John Smith'])
