from django.test import TestCase

from .models import SlugPage


class RestrictedConditionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the SlugPage model.
        
        This method creates and stores a set of test data for the SlugPage model. The data includes a series of slugs that are used to create instances of SlugPage. The slugs are created using a list of predefined values and then bulk created using the `bulk_create` method.
        
        Parameters:
        cls (cls): The class object that this method is being called on.
        
        Returns:
        None: This method does not return any value. It pop
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
