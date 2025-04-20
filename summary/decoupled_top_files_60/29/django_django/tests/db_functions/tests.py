from django.db.models import CharField, Value as V
from django.db.models.functions import Coalesce, Length, Upper
from django.test import TestCase
from django.test.utils import register_lookup

from .models import Author


class UpperBilateral(Upper):
    bilateral = True


class FunctionTests(TestCase):

    def test_nested_function_ordering(self):
        """
        Tests the ordering of a queryset based on the length of a concatenated alias or name field.
        
        This function tests the ordering of a queryset of Author objects based on the length of the alias or name field. The ordering is first by the length of the alias or name, and then by the name itself if the lengths are equal. The function uses the `Length` and `Coalesce` functions from Django's database API to determine the length of the alias or name. The test is performed twice: once
        """

        Author.objects.create(name='John Smith')
        Author.objects.create(name='Rhonda Simpson', alias='ronny')

        authors = Author.objects.order_by(Length(Coalesce('alias', 'name')))
        self.assertQuerysetEqual(
            authors, [
                'Rhonda Simpson',
                'John Smith',
            ],
            lambda a: a.name
        )

        authors = Author.objects.order_by(Length(Coalesce('alias', 'name')).desc())
        self.assertQuerysetEqual(
            authors, [
                'John Smith',
                'Rhonda Simpson',
            ],
            lambda a: a.name
        )

    def test_func_transform_bilateral(self):
        with register_lookup(CharField, UpperBilateral):
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__upper__exact='john smith')
            self.assertQuerysetEqual(
                authors.order_by('name'), [
                    'John Smith',
                ],
                lambda a: a.name
            )

    def test_func_transform_bilateral_multivalue(self):
        """
        Transform and filter authors using a bilateral lookup with an upper case comparison.
        
        This function creates two author entries in the database and then filters them using a bilateral lookup with an upper case comparison.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Registers a custom lookup `UpperBilateral` for `CharField`.
        2. Creates two author entries: 'John Smith' with alias 'smithj' and 'Rhonda' without an alias.
        3. Filters the authors where the
        """

        with register_lookup(CharField, UpperBilateral):
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__upper__in=['john smith', 'rhonda'])
            self.assertQuerysetEqual(
                authors.order_by('name'), [
                    'John Smith',
                    'Rhonda',
                ],
                lambda a: a.name
            )

    def test_function_as_filter(self):
        """
        Test the functionality of a custom filter on the 'Author' model.
        
        This function tests the filtering and exclusion of authors based on a case-insensitive alias comparison. It creates two author objects and then uses the `filter` and `exclude` methods to filter the queryset based on the alias 'smithj' (case-insensitive).
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Create two author objects: one with the alias 'SMITHJ' and another without an
        """

        Author.objects.create(name='John Smith', alias='SMITHJ')
        Author.objects.create(name='Rhonda')
        self.assertQuerysetEqual(
            Author.objects.filter(alias=Upper(V('smithj'))),
            ['John Smith'], lambda x: x.name
        )
        self.assertQuerysetEqual(
            Author.objects.exclude(alias=Upper(V('smithj'))),
            ['Rhonda'], lambda x: x.name
        )
