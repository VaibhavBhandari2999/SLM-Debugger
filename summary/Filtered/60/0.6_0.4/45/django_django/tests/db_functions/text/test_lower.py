from django.db.models import CharField
from django.db.models.functions import Lower
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class LowerTests(TestCase):

    def test_basic(self):
        """
        Tests the basic functionality of the `annotate` and `update` methods in Django ORM.
        
        This test function creates two author objects with different names and aliases. It then annotates the query with the lowercased version of the author's name and orders the results. The function asserts that the lowercased names are correctly ordered. After updating the author names to their lowercased versions, it again asserts that the names and their lowercased versions match.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input
        """

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
        Tests the transformation of a CharField using the Lower lookup.
        
        This test registers a custom lookup `Lower` for the `CharField` and creates two instances of the `Author` model. The first instance has the name 'John Smith' and the alias 'smithj', while the second instance has the name 'Rhonda'. The test then filters the `Author` objects where the lowercase version of the name is exactly 'john smith'. The result is ordered by name and compared to the expected output
        """

        with register_lookup(CharField, Lower):
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__lower__exact='john smith')
            self.assertQuerysetEqual(
                authors.order_by('name'), ['John Smith'],
                lambda a: a.name
            )
