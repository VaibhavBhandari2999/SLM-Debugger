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
        """
        Tests the ordering of authors based on the length of their name and alias.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Creates three Author objects with specified names and aliases.
        2. Orders the authors by the length of their name and then by the length of their alias.
        3. Asserts that the queryset returned matches the expected order of authors.
        
        Expected Output:
        - A list of tuples, each containing the name and alias of the authors, ordered by the length of
        """

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
        Tests the Length lookup for CharField.
        
        This function creates instances of the Author model with different names and aliases. It then filters these instances based on the length of the 'name' field. The test asserts that the queryset, when ordered by 'name', contains only the author with the name 'John Smith'.
        
        Key Parameters:
        - None
        
        Keywords:
        - register_lookup: Registers the Length lookup for CharField.
        - CharField: The field type for which the Length lookup is being tested.
        - Length
        """

        with register_lookup(CharField, Length):
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__length__gt=7)
            self.assertQuerysetEqual(
                authors.order_by('name'), ['John Smith'],
                lambda a: a.name
            )
