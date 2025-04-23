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
        
        This test registers a custom lookup `Upper` for the `CharField` and creates two instances of the `Author` model. The first instance has a name 'John Smith' and an alias 'smithj', while the second instance has a name 'Rhonda'. The test then filters the `Author` objects where the uppercased name is exactly 'JOHN SMITH'. The result is ordered by name and compared to the expected output
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
