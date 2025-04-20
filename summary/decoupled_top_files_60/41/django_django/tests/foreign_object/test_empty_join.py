from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the SlugPage model.
        
        This method creates and bulk inserts a series of SlugPage objects with predefined slugs into the database. The slugs are used to test the SlugPage model's functionality.
        
        Parameters:
        cls (cls): The class object itself, used to reference class attributes.
        
        Returns:
        None: This method does not return any value. It populates the database with test data.
        
        Example Usage:
        >>> setUpTestData()
        # The database will be populated with
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
        Test for an empty join condition in a database query.
        
        This test checks if a join operation in a database query generates an empty ON clause, which would indicate a problem with the query construction.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the join operation generates an empty ON clause.
        
        Usage:
        This test can be used to ensure that the ORM correctly handles join conditions and does not produce invalid SQL queries.
        """

        x = SlugPage.objects.get(slug='x')
        message = "Join generated an empty ON clause."
        with self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
