from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        -------------------
        A class method that sets up test data for the class. It creates a series of SlugPage objects with predefined slugs.
        
        Parameters:
        cls: The class object for which the test data is being set up.
        
        Returns:
        None: This method does not return any value. It populates the database with test data.
        
        Key Points:
        - The method uses a list of slugs to create SlugPage objects.
        - The SlugPage objects are created using
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
        x = SlugPage.objects.get(slug='x')
        message = "Join generated an empty ON clause."
        with self.assertRaisesMessage(ValueError, message):
            list(SlugPage.objects.filter(containers=x))
  list(SlugPage.objects.filter(containers=x))
