from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the SlugPage model. This method creates and bulk inserts multiple instances of SlugPage with predefined slugs.
        
        Parameters:
        cls (cls): The class object for the current test case.
        
        Returns:
        None: This method does not return any value. It populates the database with test data.
        
        Key Parameters:
        slugs (list): A list of strings representing the slugs to be created for the SlugPage instances.
        
        Example Usage:
        >>> class TestSlugPage(TestCase
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
        Tests the behavior of the filter method when used with an empty join condition.
        
        This function checks if attempting to filter a SlugPage object using an empty join condition raises a ValueError with a specific message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the join condition is empty, a ValueError is expected to be raised with the message "Join generated an empty ON clause."
        
        Usage:
        This function is typically used in a testing context to ensure that the filter method correctly handles invalid
        """

        x = SlugPage.objects.get(slug='x')
        message = "Join generated an empty ON clause."
        with self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
