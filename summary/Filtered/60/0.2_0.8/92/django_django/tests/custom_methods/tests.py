from datetime import date

from django.test import TestCase

from .models import Article


class MethodsTests(TestCase):
    def test_custom_methods(self):
        """
        Tests the custom methods of the Article model.
        
        This function creates two Article objects and tests the custom methods `was_published_today`, `articles_from_same_day_1`, and `articles_from_same_day_2`. The `was_published_today` method checks if the article was published on the current date. The `articles_from_same_day_1` and `articles_from_same_day_2` methods return a queryset of articles published on the same day as the given article.
        
        Parameters:
        - None
        
        Returns
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
