from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the SlugPage model. This method creates and bulk inserts a series of SlugPage objects with predefined slugs. The slugs are structured to form a nested hierarchy and are used for testing purposes.
        
        Parameters:
        cls (cls): The class object for which the test data is being set up.
        
        Returns:
        None: This method does not return any value. It populates the database with test data.
        
        Example Usage:
        >>> class TestSlugPage(TestCase):
        ...
        """

        slugs = [
            "a",
            "a/a",
            "a/b",
            "a/b/a",
            "x",
            "x/y/z",
        ]
        SlugPage.objects.bulk_create([SlugPage(slug=slug) for slug in slugs])

    def test_restrictions_with_no_joining_columns(self):
        """
        It's possible to create a working related field that doesn't
        use any joining columns, as long as an extra restriction is supplied.
        """
        a = SlugPage.objects.get(slug="a")
        self.assertEqual(
            [p.slug for p in SlugPage.objects.filter(ascendants=a)],
            ["a", "a/a", "a/b", "a/b/a"],
        )
        self.assertEqual(
            [p.slug for p in a.descendants.all()],
            ["a", "a/a", "a/b", "a/b/a"],
        )

        aba = SlugPage.objects.get(slug="a/b/a")
        self.assertEqual(
            [p.slug for p in SlugPage.objects.filter(descendants__in=[aba])],
            ["a", "a/b", "a/b/a"],
        )
        self.assertEqual(
            [p.slug for p in aba.ascendants.all()],
            ["a", "a/b", "a/b/a"],
        )

    def test_empty_join_conditions(self):
        """
        Tests the behavior of a query with empty join conditions.
        
        This function verifies that attempting to filter a SlugPage queryset with an empty ON clause in the join operation raises a ValueError with a specific message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the join operation does not generate an empty ON clause.
        
        Usage:
        This test case is used to ensure that the ORM correctly handles and raises an error when an empty ON clause is generated during a join operation.
        """

        x = SlugPage.objects.get(slug="x")
        message = "Join generated an empty ON clause."
        with self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
