from django.db.models import CharField
from django.db.models.functions import Upper
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class UpperTests(TestCase):

    def test_basic(self):
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
        """
        Tests the transformation of a CharField using the Upper lookup.
        
        This function creates instances of the Author model with different names and aliases. It then filters the Author objects where the name, transformed to uppercase, is exactly 'JOHN SMITH'. The result is ordered by name and compared to the expected output.
        
        Key Parameters:
        - None
        
        Keywords:
        - register_lookup: Registers the Upper lookup for CharField.
        - Author.objects.create: Creates Author objects with specified names and aliases.
        - filter: Filters the
        """

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
