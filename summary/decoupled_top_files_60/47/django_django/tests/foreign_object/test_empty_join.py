from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the SlugPage model. This method creates and bulk inserts a series of SlugPage objects with predefined slugs. The slugs are structured to form a hierarchical tree-like structure.
        
        Key Parameters:
        - None
        
        Key Parameters (for internal use):
        - slugs (list): A list of strings representing the slugs to be created.
        
        Output:
        - None. The method populates the database with the specified slugs.
        
        Example Usage:
        ```python
        class TestSlugPage(TestCase):
        """

        slugs = [
            'a',
            'a/a',
            'a/b',
            'a/b/a',
            'x',
            'x/y/z',
        ]
        SlugPage.objects.bulk_create([SlugPage(slug=slug) for slug in slugs])

    def test_restrictions_with_no_joining_columns(self):
        """
        It's possible to create a working related field that doesn't
        use any joining columns, as long as an extra restriction is supplied.
        """
        a = SlugPage.objects.get(slug='a')
        self.assertEqual(
            [p.slug for p in SlugPage.objects.filter(ascendants=a)],
            ['a', 'a/a', 'a/b', 'a/b/a'],
        )
        self.assertEqual(
            [p.slug for p in a.descendants.all()],
            ['a', 'a/a', 'a/b', 'a/b/a'],
        )

        aba = SlugPage.objects.get(slug='a/b/a')
        self.assertEqual(
            [p.slug for p in SlugPage.objects.filter(descendants__in=[aba])],
            ['a', 'a/b', 'a/b/a'],
        )
        self.assertEqual(
            [p.slug for p in aba.ascendants.all()],
            ['a', 'a/b', 'a/b/a'],
        )

    def test_empty_join_conditions(self):
        """
        Tests the behavior of the database query when joining with an empty ON clause.
        
        This function checks if attempting to filter SlugPage objects using an empty join condition raises a ValueError with a specific message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the join condition is empty, a ValueError is expected to be raised with the message "Join generated an empty ON clause."
        
        Usage:
        This function is typically used in a testing context to ensure that the database query handling correctly identifies and
        """

        x = SlugPage.objects.get(slug='x')
        message = "Join generated an empty ON clause."
        with self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
