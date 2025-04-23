from django.db.models import CharField
from django.db.models.functions import Length
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class LengthTests(TestCase):

    def test_basic(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(
            name_length=Length('name'),
            alias_length=Length('alias'),
        )
        self.assertQuerysetEqual(
            authors.order_by('name'), [(10, 6), (6, None)],
            lambda a: (a.name_length, a.alias_length)
        )
        self.assertEqual(authors.filter(alias_length__lte=Length('name')).count(), 1)

    def test_ordering(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='John Smith', alias='smithj1')
        Author.objects.create(name='Rhonda', alias='ronny')
        authors = Author.objects.order_by(Length('name'), Length('alias'))
        self.assertQuerysetEqual(
            authors, [
                ('Rhonda', 'ronny'),
                ('John Smith', 'smithj'),
                ('John Smith', 'smithj1'),
            ],
            lambda a: (a.name, a.alias)
        )

    def test_transform(self):
        """
        Tests the transformation of a CharField using the Length lookup.
        
        This function creates instances of the Author model with different names and aliases. It then filters the authors based on the length of their names, specifically selecting those with a name length greater than 7 characters. The filtered queryset is ordered by name and compared to the expected result.
        
        Key Parameters:
        - None
        
        Keywords:
        - register_lookup: Registers the Length lookup for CharField.
        - Author: Model being tested.
        - name: Field of the Author
        """

        with register_lookup(CharField, Length):
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__length__gt=7)
            self.assertQuerysetEqual(
                authors.order_by('name'), ['John Smith'],
                lambda a: a.name
            )
me
            )
