from datetime import date

from django.test import TestCase

from .models import Article


class MethodsTests(TestCase):
    def test_custom_methods(self):
        """
        Tests for custom methods in the Article model.
        
        This function tests the custom methods `was_published_today`, `articles_from_same_day_1`, and `articles_from_same_day_2` of the Article model. It creates two instances of the Article model with different headlines and pub_date. The function then checks if the `was_published_today` method returns False for the first article and True for the second. It also verifies that the `articles_from_same_day_1` and `articles_from_same_day
        """

        a = Article.objects.create(
            headline="Parrot programs in Python", pub_date=date(2005, 7, 27)
        )
        b = Article.objects.create(
            headline="Beatles reunite", pub_date=date(2005, 7, 27)
        )

        self.assertFalse(a.was_published_today())
        self.assertQuerysetEqual(
            a.articles_from_same_day_1(), [
                "Beatles reunite",
            ],
            lambda a: a.headline,
        )
        self.assertQuerysetEqual(
            a.articles_from_same_day_2(), [
                "Beatles reunite",
            ],
            lambda a: a.headline
        )

        self.assertQuerysetEqual(
            b.articles_from_same_day_1(), [
                "Parrot programs in Python",
            ],
            lambda a: a.headline,
        )
        self.assertQuerysetEqual(
            b.articles_from_same_day_2(), [
                "Parrot programs in Python",
            ],
            lambda a: a.headline
        )
