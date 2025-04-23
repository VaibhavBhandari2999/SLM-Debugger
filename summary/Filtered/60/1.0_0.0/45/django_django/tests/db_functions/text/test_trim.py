from django.db.models import CharField
from django.db.models.functions import LTrim, RTrim, Trim
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class TrimTests(TestCase):
    def test_trim(self):
        """
        Tests the functionality of the LTrim, RTrim, and Trim functions in the Author model.
        
        This test function creates two Author objects with specific names and aliases. It then uses the annotate method to apply LTrim, RTrim, and Trim functions to the 'name' field of the Author model. The test asserts that the trimmed names are correctly returned when the queryset is ordered by the alias field.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Assertions:
        - The queryset is ordered by
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
