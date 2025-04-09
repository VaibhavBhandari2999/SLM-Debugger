from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the SlugPage model by creating a list of slugs and bulk creating corresponding SlugPage objects.
        
        Summary:
        - Input: None
        - Output: None
        - Important Functions: `bulk_create`, `SlugPage`
        - Keywords: `setUpTestData`, `slugs`, `SlugPage`
        
        Args:
        - cls: The class object where this method is defined.
        
        Returns:
        - None
        
        Example Usage:
        ```python
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
        Test that a join with no valid conditions raises a ValueError.
        
        This function tests whether attempting to filter `SlugPage` objects
        related to a specific `SlugPage` instance through a non-existent
        relationship (i.e., using an empty join condition) results in a
        `ValueError` being raised with a specific error message.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the join operation does not generate any valid
        conditions
        """

        x = SlugPage.objects.get(slug='x')
        message = "Join generated an empty ON clause."
        with self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
