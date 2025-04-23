from django.db import connection
from django.db.models import CharField
from django.db.models.functions import SHA384
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class SHA384Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Author model.
        
        This method creates and bulk inserts multiple instances of the Author model into the database. It is intended to be used as a class method for test cases.
        
        Parameters:
        cls (cls): The test case class itself, used to access class attributes.
        
        Returns:
        None: This method does not return any value. It populates the database with test data.
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
        Tests the basic functionality of the Author model's SHA384 alias generation.
        
        This test function checks if the SHA384 hash of the 'alias' field correctly generates unique hashes for each author. The test involves the following steps:
        1. Annotates the 'Author' model instances with a new field 'sha384_alias' which is the SHA384 hash of the 'alias' field.
        2. Retrieves the values of the 'sha384_alias' field
        """

        authors = Author.objects.annotate(
            sha384_alias=SHA384('alias'),
        ).values_list('sha384_alias', flat=True).order_by('pk')
        self.assertSequenceEqual(
            authors,
            [
                '9df976bfbcf96c66fbe5cba866cd4deaa8248806f15b69c4010a404112906e4ca7b57e53b9967b80d77d4f5c2982cbc8',
                '72202c8005492016cc670219cce82d47d6d2d4273464c742ab5811d691b1e82a7489549e3a73ffa119694f90678ba2e3',
                'eda87fae41e59692c36c49e43279c8111a00d79122a282a944e8ba9a403218f049a48326676a43c7ba378621175853b0',
                '38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da274edebfe76f65fbd51ad2f14898b95b',
                '38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da274edebfe76f65fbd51ad2f14898b95b'
                if connection.features.interprets_empty_strings_as_nulls else None,
            ],
        )

    def test_transform(self):
        """
        Tests the transformation of a CharField using the SHA384 lookup.
        
        This function registers a custom lookup for the CharField and filters the Author objects based on a SHA384 hash of the alias field. It then checks if the filtered aliases match the expected result.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - No external parameters are passed to this function.
        
        Keywords:
        - No keywords are used in this function.
        
        Input:
        - The function uses a predefined
        """

        with register_lookup(CharField, SHA384):
            authors = Author.objects.filter(
                alias__sha384=(
                    '9df976bfbcf96c66fbe5cba866cd4deaa8248806f15b69c4010a404112906e4ca7b57e53b9967b80d77d4f5c2982cbc8'
                ),
            ).values_list('alias', flat=True)
            self.assertSequenceEqual(authors, ['John Smith'])
