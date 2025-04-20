from django.db.models import CharField
from django.db.models.functions import Lower
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class LowerTests(TestCase):

    def test_basic(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(lower_name=Lower('name'))
        self.assertQuerysetEqual(
            authors.order_by('name'), ['john smith', 'rhonda'],
            lambda a: a.lower_name
        )
        Author.objects.update(name=Lower('name'))
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                ('john smith', 'john smith'),
                ('rhonda', 'rhonda'),
            ],
            lambda a: (a.lower_name, a.name)
        )

    def test_num_args(self):
        with self.assertRaisesMessage(TypeError, "'Lower' takes exactly 1 argument (2 given)"):
            Author.objects.update(name=Lower('name', 'name'))

    def test_transform(self):
        """
        Tests the transformation of a CharField to lowercase using a custom lookup.
        
        This function registers a custom lookup 'Lower' for the CharField, creates two instances of the Author model with different names and aliases, and then filters the authors based on a lowercase transformation of the name field. The result is then compared to the expected output.
        
        Key Parameters:
        - None
        
        Keywords:
        - register_lookup: Registers a custom lookup for CharField.
        - Author.objects.create: Creates instances of the Author model.
        - name
        """

        with register_lookup(CharField, Lower):
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__lower__exact='john smith')
            self.assertQuerysetEqual(
                authors.order_by('name'), ['John Smith'],
                lambda a: a.name
            )
