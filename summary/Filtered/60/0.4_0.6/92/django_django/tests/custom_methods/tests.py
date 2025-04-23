from datetime import date

from django.test import TestCase

from .models import Article


class MethodsTests(TestCase):
    def test_custom_methods(self):
        """
        Tests the custom methods of the Article model.
        
        This function creates two instances of the Article model with different headlines and publication dates. It then tests the custom methods `was_published_today`, `articles_from_same_day_1`, and `articles_from_same_day_2` to ensure they return the expected results.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Methods:
        - `was_published_today()`: Checks if the article was published on the current date.
        - `articles_from_same_day_1
        """

        a = Article.objects.create(
            headline="Parrot programs in Python", pub_date=date(2005, 7, 27)
        )
        b = Article.objects.create(
            headline="Beatles reunite", pub_date=date(2005, 7, 27)
        )

        self.assertFalse(a.was_published_today())
        self.assertQuerysetEqual(
            a.articles_from_same_day_1(),
            [
                "Beatles reunite",
            ],
            lambda a: a.headline,
        )
        self.assertQuerysetEqual(
            a.articles_from_same_day_2(),
            [
                "Beatles reunite",
            ],
            lambda a: a.headline,
        )

        self.assertQuerysetEqual(
            b.articles_from_same_day_1(),
            [
                "Parrot programs in Python",
            ],
            lambda a: a.headline,
        )
        self.assertQuerysetEqual(
            b.articles_from_same_day_2(),
            [
                "Parrot programs in Python",
            ],
            lambda a: a.headline,
        )
