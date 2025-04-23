from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the SlugPage model.
        
        This method creates and initializes a set of test data for the SlugPage model. It uses a list of slugs to create instances of SlugPage and bulk creates them in the database.
        
        Key Parameters:
        - None
        
        Key Attributes:
        - slugs (list): A list of slugs used to create SlugPage instances.
        
        Output:
        - None. The method directly modifies the database by creating instances of SlugPage.
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
        Tests the behavior of the database query when attempting to filter using an empty join condition.
        
        This function checks if a ValueError is raised when trying to filter `SlugPage` objects using an empty ON clause in the join condition. It expects the join to fail and raise a ValueError with a specific message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the join condition is empty and no exception is raised.
        
        Example:
        >>> test_empty_join_conditions()
        ValueError: Join generated
        """

        x = SlugPage.objects.get(slug="x")
        message = "Join generated an empty ON clause."
        with self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
