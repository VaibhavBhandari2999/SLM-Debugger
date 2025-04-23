from django.db.models import CharField, Value as V
from django.db.models.functions import Lower, StrIndex, Substr, Upper
from django.test import TestCase

from ..models import Author


class SubstrTests(TestCase):

    def test_basic(self):
        """
        Tests the functionality of the Substr and Lower functions in the Author model.
        
        This test function creates instances of the Author model with different names and aliases. It then uses the Substr function to extract substrings from the 'name' field and the Lower function to convert the first 5 characters of the 'name' field to lowercase. The test function asserts that the extracted substrings and the updated aliases match the expected values.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        -
        """

        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(name_part=Substr('name', 5, 3))
        self.assertQuerysetEqual(
            authors.order_by('name'), [' Sm', 'da'],
            lambda a: a.name_part
        )
        authors = Author.objects.annotate(name_part=Substr('name', 2))
        self.assertQuerysetEqual(
            authors.order_by('name'), ['ohn Smith', 'honda'],
            lambda a: a.name_part
        )
        # If alias is null, set to first 5 lower characters of the name.
        Author.objects.filter(alias__isnull=True).update(
            alias=Lower(Substr('name', 1, 5)),
        )
        self.assertQuerysetEqual(
            authors.order_by('name'), ['smithj', 'rhond'],
            lambda a: a.alias
        )

    def test_start(self):
        Author.objects.create(name='John Smith', alias='smithj')
        a = Author.objects.annotate(
            name_part_1=Substr('name', 1),
            name_part_2=Substr('name', 2),
        ).get(alias='smithj')

        self.assertEqual(a.name_part_1[1:], a.name_part_2)

    def test_pos_gt_zero(self):
        with self.assertRaisesMessage(ValueError, "'pos' must be greater than 0"):
            Author.objects.annotate(raises=Substr('name', 0))

    def test_expressions(self):
        """
        Tests the functionality of the Substr, Upper, StrIndex, and CharField functions in Django ORM.
        
        This test creates two author objects and uses the Substr, Upper, StrIndex, and CharField functions to extract and manipulate a part of the 'name' field. The resulting queryset is then ordered by the 'name' field and compared to the expected output.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - A list of strings representing the
        """

        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        substr = Substr(Upper('name'), StrIndex('name', V('h')), 5, output_field=CharField())
        authors = Author.objects.annotate(name_part=substr)
        self.assertQuerysetEqual(
            authors.order_by('name'), ['HN SM', 'HONDA'],
            lambda a: a.name_part
        )
art
        )
