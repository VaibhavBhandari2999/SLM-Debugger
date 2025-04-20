from django.db.models import Value as V
from django.db.models.functions import Lower, StrIndex, Substr, Upper
from django.test import TestCase

from ..models import Author


class SubstrTests(TestCase):

    def test_basic(self):
        """
        Tests basic functionality of the Substr and Lower functions in Django ORM.
        
        This test function checks the following:
        1. Creates two author objects with different names.
        2. Annotates the author objects with a substring of their name starting from the 5th character and having a length of 3.
        3. Orders the annotated objects by their names and checks if the substrings match [' Sm', 'da'].
        4. Annotates the author objects with a substring of their name starting from the
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
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        substr = Substr(Upper('name'), StrIndex('name', V('h')), 5)
        authors = Author.objects.annotate(name_part=substr)
        self.assertQuerysetEqual(
            authors.order_by('name'), ['HN SM', 'HONDA'],
            lambda a: a.name_part
        )
