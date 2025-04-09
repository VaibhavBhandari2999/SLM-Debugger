from django.test import TestCase

from .models import (
    Event, Movie, Package, PackageNullFK, Person, Screening, ScreeningNullFK,
)


# These are tests for #16715. The basic scheme is always the same: 3 models with
# 2 relations. The first relation may be null, while the second is non-nullable.
# In some cases, Django would pick the wrong join type for the second relation,
# resulting in missing objects in the queryset.
#
#   Model A
#   | (Relation A/B : nullable)
#   Model B
#   | (Relation B/C : non-nullable)
#   Model C
#
# Because of the possibility of NULL rows resulting from the LEFT OUTER JOIN
# between Model A and Model B (i.e. instances of A without reference to B),
# the second join must also be LEFT OUTER JOIN, so that we do not ignore
# instances of A that do not reference B.
#
# Relation A/B can either be an explicit foreign key or an implicit reverse
# relation such as introduced by one-to-one relations (through multi-table
# inheritance).
class NestedForeignKeysTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.director = Person.objects.create(name='Terry Gilliam / Terry Jones')
        cls.movie = Movie.objects.create(title='Monty Python and the Holy Grail', director=cls.director)

    # This test failed in #16715 because in some cases INNER JOIN was selected
    # for the second foreign key relation instead of LEFT OUTER JOIN.
    def test_inheritance(self):
        """
        Tests inheritance-related functionality of the Event model.
        
        This function creates instances of the Event and Screening models, then performs various queries to test inheritance and related object access. It checks the count of objects returned by different query methods, including those using `select_related` and `values`.
        
        Args:
        None
        
        Returns:
        None
        """

        Event.objects.create()
        Screening.objects.create(movie=self.movie)

        self.assertEqual(len(Event.objects.all()), 2)
        self.assertEqual(len(Event.objects.select_related('screening')), 2)
        # This failed.
        self.assertEqual(len(Event.objects.select_related('screening__movie')), 2)

        self.assertEqual(len(Event.objects.values()), 2)
        self.assertEqual(len(Event.objects.values('screening__pk')), 2)
        self.assertEqual(len(Event.objects.values('screening__movie__pk')), 2)
        self.assertEqual(len(Event.objects.values('screening__movie__title')), 2)
        # This failed.
        self.assertEqual(len(Event.objects.values('screening__movie__pk', 'screening__movie__title')), 2)

        # Simple filter/exclude queries for good measure.
        self.assertEqual(Event.objects.filter(screening__movie=self.movie).count(), 1)
        self.assertEqual(Event.objects.exclude(screening__movie=self.movie).count(), 1)

    # These all work because the second foreign key in the chain has null=True.
    def test_inheritance_null_FK(self):
        """
        Tests inheritance with null foreign key relationships.
        
        This function creates instances of `Event` and `ScreeningNullFK` models, and then performs various queries on them using different query methods such as `select_related`, `values`, `filter`, and `exclude`. The important keywords and functions used include:
        
        - `Event.objects.create()`: Creates an instance of the `Event` model.
        - `ScreeningNullFK.objects.create(movie=None)`: Creates an instance of the `Screening
        """

        Event.objects.create()
        ScreeningNullFK.objects.create(movie=None)
        ScreeningNullFK.objects.create(movie=self.movie)

        self.assertEqual(len(Event.objects.all()), 3)
        self.assertEqual(len(Event.objects.select_related('screeningnullfk')), 3)
        self.assertEqual(len(Event.objects.select_related('screeningnullfk__movie')), 3)

        self.assertEqual(len(Event.objects.values()), 3)
        self.assertEqual(len(Event.objects.values('screeningnullfk__pk')), 3)
        self.assertEqual(len(Event.objects.values('screeningnullfk__movie__pk')), 3)
        self.assertEqual(len(Event.objects.values('screeningnullfk__movie__title')), 3)
        self.assertEqual(len(Event.objects.values('screeningnullfk__movie__pk', 'screeningnullfk__movie__title')), 3)

        self.assertEqual(Event.objects.filter(screeningnullfk__movie=self.movie).count(), 1)
        self.assertEqual(Event.objects.exclude(screeningnullfk__movie=self.movie).count(), 2)

    def test_null_exclude(self):
        """
        Tests the `exclude` method with a null foreign key.
        
        This function creates two instances of `ScreeningNullFK`: one with a null movie and another with a non-null movie. It then uses the `exclude` method to filter out the instance with the non-null movie, ensuring that only the instance with the null movie is returned.
        
        Args:
        None
        
        Returns:
        None
        """

        screening = ScreeningNullFK.objects.create(movie=None)
        ScreeningNullFK.objects.create(movie=self.movie)
        self.assertEqual(
            list(ScreeningNullFK.objects.exclude(movie__id=self.movie.pk)),
            [screening])

    # This test failed in #16715 because in some cases INNER JOIN was selected
    # for the second foreign key relation instead of LEFT OUTER JOIN.
    def test_explicit_ForeignKey(self):
        """
        Tests the behavior of explicit ForeignKey relationships in Django ORM.
        
        This function creates instances of `Package` and `Screening` models, and tests various queries involving these models. It checks the count of objects returned by different query methods, including those with `select_related`, `values`, and filtering based on related fields.
        
        Args:
        None
        
        Returns:
        None
        """

        Package.objects.create()
        screening = Screening.objects.create(movie=self.movie)
        Package.objects.create(screening=screening)

        self.assertEqual(len(Package.objects.all()), 2)
        self.assertEqual(len(Package.objects.select_related('screening')), 2)
        self.assertEqual(len(Package.objects.select_related('screening__movie')), 2)

        self.assertEqual(len(Package.objects.values()), 2)
        self.assertEqual(len(Package.objects.values('screening__pk')), 2)
        self.assertEqual(len(Package.objects.values('screening__movie__pk')), 2)
        self.assertEqual(len(Package.objects.values('screening__movie__title')), 2)
        # This failed.
        self.assertEqual(len(Package.objects.values('screening__movie__pk', 'screening__movie__title')), 2)

        self.assertEqual(Package.objects.filter(screening__movie=self.movie).count(), 1)
        self.assertEqual(Package.objects.exclude(screening__movie=self.movie).count(), 1)

    # These all work because the second foreign key in the chain has null=True.
    def test_explicit_ForeignKey_NullFK(self):
        """
        Tests the behavior of explicit ForeignKey relationships with NULL values using `select_related` and `values` methods.
        
        This function creates instances of `PackageNullFK` and `ScreeningNullFK` models, where `ScreeningNullFK` has an optional `movie` field and an optional `screening` field that references `PackageNullFK`. It then performs various queries to check the correct handling of NULL values and relationships.
        
        Important Functions:
        - `objects.create()`: Creates new model
        """

        PackageNullFK.objects.create()
        screening = ScreeningNullFK.objects.create(movie=None)
        screening_with_movie = ScreeningNullFK.objects.create(movie=self.movie)
        PackageNullFK.objects.create(screening=screening)
        PackageNullFK.objects.create(screening=screening_with_movie)

        self.assertEqual(len(PackageNullFK.objects.all()), 3)
        self.assertEqual(len(PackageNullFK.objects.select_related('screening')), 3)
        self.assertEqual(len(PackageNullFK.objects.select_related('screening__movie')), 3)

        self.assertEqual(len(PackageNullFK.objects.values()), 3)
        self.assertEqual(len(PackageNullFK.objects.values('screening__pk')), 3)
        self.assertEqual(len(PackageNullFK.objects.values('screening__movie__pk')), 3)
        self.assertEqual(len(PackageNullFK.objects.values('screening__movie__title')), 3)
        self.assertEqual(len(PackageNullFK.objects.values('screening__movie__pk', 'screening__movie__title')), 3)

        self.assertEqual(PackageNullFK.objects.filter(screening__movie=self.movie).count(), 1)
        self.assertEqual(PackageNullFK.objects.exclude(screening__movie=self.movie).count(), 2)


# Some additional tests for #16715. The only difference is the depth of the
# nesting as we now use 4 models instead of 3 (and thus 3 relations). This
# checks if promotion of join types works for deeper nesting too.
class DeeplyNestedForeignKeysTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.director = Person.objects.create(name='Terry Gilliam / Terry Jones')
        cls.movie = Movie.objects.create(title='Monty Python and the Holy Grail', director=cls.director)

    def test_inheritance(self):
        """
        Tests inheritance behavior of Event model with related objects.
        
        This function creates instances of `Event` and `Screening` models, then performs various queries on the `Event` model to verify its inheritance and related object handling capabilities. The important functions used include `create`, `select_related`, `values`, `filter`, and `exclude`.
        
        Args:
        None
        
        Returns:
        None
        """

        Event.objects.create()
        Screening.objects.create(movie=self.movie)

        self.assertEqual(len(Event.objects.all()), 2)
        self.assertEqual(len(Event.objects.select_related('screening__movie__director')), 2)

        self.assertEqual(len(Event.objects.values()), 2)
        self.assertEqual(len(Event.objects.values('screening__movie__director__pk')), 2)
        self.assertEqual(len(Event.objects.values('screening__movie__director__name')), 2)
        self.assertEqual(
            len(Event.objects.values('screening__movie__director__pk', 'screening__movie__director__name')),
            2
        )
        self.assertEqual(len(Event.objects.values('screening__movie__pk', 'screening__movie__director__pk')), 2)
        self.assertEqual(len(Event.objects.values('screening__movie__pk', 'screening__movie__director__name')), 2)
        self.assertEqual(len(Event.objects.values('screening__movie__title', 'screening__movie__director__pk')), 2)
        self.assertEqual(len(Event.objects.values('screening__movie__title', 'screening__movie__director__name')), 2)

        self.assertEqual(Event.objects.filter(screening__movie__director=self.director).count(), 1)
        self.assertEqual(Event.objects.exclude(screening__movie__director=self.director).count(), 1)

    def test_explicit_ForeignKey(self):
        """
        Tests the behavior of explicit ForeignKey relationships in Django ORM.
        
        This test method creates instances of `Package` and `Screening` models, and verifies the following:
        - The count of all `Package` objects after creation.
        - The count of `Package` objects with selected related fields (`screening__movie__director`).
        - The count of `Package` objects with various values queries.
        - Filtering and excluding packages based on the director of the movie associated with the screening.
        """

        Package.objects.create()
        screening = Screening.objects.create(movie=self.movie)
        Package.objects.create(screening=screening)

        self.assertEqual(len(Package.objects.all()), 2)
        self.assertEqual(len(Package.objects.select_related('screening__movie__director')), 2)

        self.assertEqual(len(Package.objects.values()), 2)
        self.assertEqual(len(Package.objects.values('screening__movie__director__pk')), 2)
        self.assertEqual(len(Package.objects.values('screening__movie__director__name')), 2)
        self.assertEqual(
            len(Package.objects.values('screening__movie__director__pk', 'screening__movie__director__name')),
            2
        )
        self.assertEqual(len(Package.objects.values('screening__movie__pk', 'screening__movie__director__pk')), 2)
        self.assertEqual(len(Package.objects.values('screening__movie__pk', 'screening__movie__director__name')), 2)
        self.assertEqual(len(Package.objects.values('screening__movie__title', 'screening__movie__director__pk')), 2)
        self.assertEqual(len(Package.objects.values('screening__movie__title', 'screening__movie__director__name')), 2)

        self.assertEqual(Package.objects.filter(screening__movie__director=self.director).count(), 1)
        self.assertEqual(Package.objects.exclude(screening__movie__director=self.director).count(), 1)
