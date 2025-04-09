"""
The provided Python file contains unit tests for the `Author` model in a Django application. It primarily focuses on testing the `Substr` function from Django's database functions module. The tests cover various scenarios such as basic substring extraction, handling null values, and combining multiple string functions.

#### Main Classes and Functions:
- **`SubstrTests`**: A test case class that defines several test methods to validate the behavior of the `Substr` function.
  - **`test_basic`**: Tests basic functionality including substring extraction, ordering, and updating fields based on substrings.
  - **`test_start`**: Tests the extraction of a substring starting from the second character of the name.
  - **`test_pos_gt_zero`**:
"""
from django.db.models import CharField, Value as V
from django.db.models.functions import Lower, StrIndex, Substr, Upper
from django.test import TestCase

from ..models import Author


class SubstrTests(TestCase):

    def test_basic(self):
        """
        Tests basic functionality of the Author model and its annotations.
        
        - Creates two Author objects with different names.
        - Annotates the Author queryset with substrings of the 'name' field.
        - Orders and compares the annotated queryset with expected results.
        - Updates the 'alias' field for Author objects where 'alias' is null using a substring of the 'name' field.
        - Verifies the updated 'alias' values match the expected results.
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
        """
        Tests the Substr function by creating an author with the name 'John Smith' and alias 'smithj'. It then queries the database to retrieve the author and checks if the first character of the name (excluding the first character) is equal to the rest of the name.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `Author.objects.create`: Creates a new author instance with the specified name and alias.
        - `Substr`: Extracts a substring
        """

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
        Tests the functionality of the Substr, Upper, StrIndex, and annotate methods by creating author objects, extracting a substring from the 'name' field after the first occurrence of 'h', and ordering the results alphabetically.
        
        - Creates two author objects with different names.
        - Uses the `Substr`, `Upper`, and `StrIndex` functions to extract a 5-character substring starting from the first occurrence of 'h' in the 'name' field.
        - Annotates
        """

        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        substr = Substr(Upper('name'), StrIndex('name', V('h')), 5, output_field=CharField())
        authors = Author.objects.annotate(name_part=substr)
        self.assertQuerysetEqual(
            authors.order_by('name'), ['HN SM', 'HONDA'],
            lambda a: a.name_part
        )
