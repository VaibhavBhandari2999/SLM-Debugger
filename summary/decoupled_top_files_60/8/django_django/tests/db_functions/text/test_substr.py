from django.db.models import CharField, Value as V
from django.db.models.functions import Lower, StrIndex, Substr, Upper
from django.test import TestCase

from ..models import Author


class SubstrTests(TestCase):

    def test_basic(self):
        """
        Tests basic functionality of the Substr and Lower functions in Django ORM.
        
        This test function performs several operations on the Author model:
        1. Creates two Author objects with different names.
        2. Annotates the Author queryset with a substring of the 'name' field from the 5th character to the 7th character.
        3. Orders the annotated queryset by the 'name' field and checks if the substring matches the expected values.
        4. Annotates the Author queryset with a substring of the
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
        Tests the functionality of the Substr, Upper, StrIndex, and output_field functions in Django ORM.
        
        This test creates two author objects and uses the Substr, Upper, StrIndex, and output_field functions to extract a substring from the 'name' field starting from the position where 'h' is found, with a length of 5 characters. The results are then annotated to the 'name_part' field and ordered by the 'name' field. The test asserts that the 'name_part
        """

        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        substr = Substr(Upper('name'), StrIndex('name', V('h')), 5, output_field=CharField())
        authors = Author.objects.annotate(name_part=substr)
        self.assertQuerysetEqual(
            authors.order_by('name'), ['HN SM', 'HONDA'],
            lambda a: a.name_part
        )
