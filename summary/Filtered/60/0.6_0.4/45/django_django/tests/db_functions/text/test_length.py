from django.db.models import CharField
from django.db.models.functions import Length
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class LengthTests(TestCase):

    def test_basic(self):
        """
        Tests the functionality of the Length annotation in Django ORM.
        
        This test function creates two Author objects with different names and aliases. It then annotates the queryset with the lengths of the 'name' and 'alias' fields. The test asserts that the queryset is ordered correctly by name and that the count of authors with an alias length less than or equal to their name length is one.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - Assertions are made to
        """

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
        Tests the transformation of a CharField using a custom lookup (Length).
        
        This function creates instances of the Author model with different names and aliases. It then filters the authors based on the length of their names, specifically selecting those with a name length greater than 7 characters. The results are ordered by name and compared to the expected output.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Registers a custom lookup for CharField named 'Length'.
        2. Creates two Author objects:
        """

        with register_lookup(CharField, Length):
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__length__gt=7)
            self.assertQuerysetEqual(
                authors.order_by('name'), ['John Smith'],
                lambda a: a.name
            )
