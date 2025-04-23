from django.db.models import CharField
from django.db.models.functions import Upper
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class UpperTests(TestCase):

    def test_basic(self):
        """
        Tests the basic functionality of the `Upper` function in Django ORM.
        
        This test function creates two instances of the `Author` model with different names. It then annotates the query with the uppercase version of the name and asserts that the query results are as expected. The test also updates the names to their uppercase versions and checks the updated results.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - The function asserts that the query results match the expected uppercase
        """

        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(upper_name=Upper('name'))
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                'JOHN SMITH',
                'RHONDA',
            ],
            lambda a: a.upper_name
        )
        Author.objects.update(name=Upper('name'))
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                ('JOHN SMITH', 'JOHN SMITH'),
                ('RHONDA', 'RHONDA'),
            ],
            lambda a: (a.upper_name, a.name)
        )

    def test_transform(self):
        with register_lookup(CharField, Upper):
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__upper__exact='JOHN SMITH')
            self.assertQuerysetEqual(
                authors.order_by('name'), [
                    'John Smith',
                ],
                lambda a: a.name
            )
