from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the SlugPage model.
        
        This method creates and initializes test data for the SlugPage model by bulk creating instances with predefined slugs. The slugs are stored in a list and used to create SlugPage objects.
        
        Parameters:
        cls (cls): The class object for the current test case.
        
        Returns:
        None: This method does not return anything. It populates the database with test data.
        
        Example Usage:
        >>> class TestSlugPage(TestCase):
        >>>     @classmethod
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
        Test for an empty join condition in a database query.
        
        This function checks if attempting to filter a SlugPage object by a non-existent
        join condition raises a ValueError with a specific message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the join condition is empty, a ValueError is raised with
        the message "Join generated an empty ON clause."
        
        Usage:
        This test function is used to ensure that the database query correctly
        handles the case where a join condition
        """

        x = SlugPage.objects.get(slug="x")
        message = "Join generated an empty ON clause."
        with self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
