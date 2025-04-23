from django.db.models import CharField
from django.db.models.functions import Upper
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class UpperTests(TestCase):

    def test_basic(self):
        """
        Tests the basic functionality of the `Upper` function in Django ORM.
        
        This test function creates two `Author` objects with different names. It then annotates the `Author` queryset with the upper-cased version of the `name` field. The test checks if the annotated queryset is ordered correctly and if the upper-cased names match the expected output. After updating the `name` field to its upper-cased version, the test verifies that the updated names are consistent with the original upper-cased
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
          'John Smith',
                ],
                lambda a: a.name
            )
