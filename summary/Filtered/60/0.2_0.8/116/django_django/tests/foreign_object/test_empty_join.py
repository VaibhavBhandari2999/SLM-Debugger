from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        This method sets up test data for the tests in the class. It is a class method that is called once before any tests are run.
        
        Parameters:
        cls (cls): The test class itself, used to create and store the test data.
        
        Returns:
        None
        
        Key Data Points:
        - Generates a list of slugs for testing.
        - Creates and bulk inserts SlugPage objects with the given slugs.
        - The slugs created are:
        - "a"
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
        x = SlugPage.objects.get(slug="x")
        message = "Join generated an empty ON clause."
        with self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
h self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
