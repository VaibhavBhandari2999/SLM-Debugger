from django.db.models import CharField
from django.db.models.functions import LTrim, RTrim, Trim
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class TrimTests(TestCase):
    def test_trim(self):
        """
        Tests the functionality of LTrim, RTrim, and Trim functions on the 'name' field of Author objects. Creates two Author instances with specific names and aliases, then annotates the queryset with left-trimmed, right-trimmed, and trimmed versions of the 'name' field. Asserts that the ordered queryset matches the expected results.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `LTrim`: Left-trims whitespace from the 'name
        """

        Author.objects.create(name='  John ', alias='j')
        Author.objects.create(name='Rhonda', alias='r')
        authors = Author.objects.annotate(
            ltrim=LTrim('name'),
            rtrim=RTrim('name'),
            trim=Trim('name'),
        )
        self.assertQuerysetEqual(
            authors.order_by('alias'), [
                ('John ', '  John', 'John'),
                ('Rhonda', 'Rhonda', 'Rhonda'),
            ],
            lambda a: (a.ltrim, a.rtrim, a.trim)
        )

    def test_trim_transform(self):
        """
        Tests the functionality of different string transformation functions (LTrim, RTrim, Trim) on the 'name' field of the Author model. Creates two author instances with specific names, then filters and asserts that the correct author is returned based on the applied transformation.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `Author.objects.create`: Creates new author instances with specified names.
        - `register_lookup`: Registers custom lookups for CharField.
        - `
        """

        Author.objects.create(name=' John  ')
        Author.objects.create(name='Rhonda')
        tests = (
            (LTrim, 'John  '),
            (RTrim, ' John'),
            (Trim, 'John'),
        )
        for transform, trimmed_name in tests:
            with self.subTest(transform=transform):
                with register_lookup(CharField, transform):
                    authors = Author.objects.filter(**{'name__%s' % transform.lookup_name: trimmed_name})
                    self.assertQuerysetEqual(authors, [' John  '], lambda a: a.name)
