from django.db.models import FilteredRelation
from django.test import TestCase

from .models import Organiser, Pool, PoolStyle, Tournament


class ExistingRelatedInstancesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for tournament-related models.
        
        This method creates instances of `Tournament`, `Organiser`, `Pool`, and `PoolStyle` models and assigns them to class attributes. The important keywords and functions used include:
        
        - `Tournament`: Creates a tournament instance with a specified name.
        - `Organiser`: Creates an organiser instance with a specified name.
        - `Pool`: Creates a pool instance associated with a specific tournament and organiser.
        - `Pool
        """

        cls.t1 = Tournament.objects.create(name="Tourney 1")
        cls.t2 = Tournament.objects.create(name="Tourney 2")
        cls.o1 = Organiser.objects.create(name="Organiser 1")
        cls.p1 = Pool.objects.create(
            name="T1 Pool 1", tournament=cls.t1, organiser=cls.o1
        )
        cls.p2 = Pool.objects.create(
            name="T1 Pool 2", tournament=cls.t1, organiser=cls.o1
        )
        cls.p3 = Pool.objects.create(
            name="T2 Pool 1", tournament=cls.t2, organiser=cls.o1
        )
        cls.p4 = Pool.objects.create(
            name="T2 Pool 2", tournament=cls.t2, organiser=cls.o1
        )
        cls.ps1 = PoolStyle.objects.create(name="T1 Pool 2 Style", pool=cls.p2)
        cls.ps2 = PoolStyle.objects.create(name="T2 Pool 1 Style", pool=cls.p3)
        cls.ps3 = PoolStyle.objects.create(
            name="T1 Pool 1/3 Style", pool=cls.p1, another_pool=cls.p3
        )

    def test_foreign_key(self):
        """
        Tests the foreign key relationship between a Tournament and its Pool.
        
        This function asserts that the `tournament` object is the same as the `tournament`
        attribute of the first `pool` object associated with the given `Tournament`.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the `tournament` object is not the same as the `tournament`
        attribute of the first `pool` object.
        
        SQL Queries:
        - 2 queries are
        """

        with self.assertNumQueries(2):
            tournament = Tournament.objects.get(pk=self.t1.pk)
            pool = tournament.pool_set.all()[0]
            self.assertIs(tournament, pool.tournament)

    def test_foreign_key_prefetch_related(self):
        """
        Retrieve a tournament with its associated pools using prefetch_related.
        
        This method fetches a specific tournament by its primary key (pk) and
        prefetches its related pool sets. It then accesses the first pool from
        the prefetch-related query and checks if the tournament is correctly
        linked as the pool's tournament.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        DoesNotExist: If no tournament with the given primary key exists.
        MultipleObjectsReturned: If
        """

        with self.assertNumQueries(2):
            tournament = Tournament.objects.prefetch_related("pool_set").get(
                pk=self.t1.pk
            )
            pool = tournament.pool_set.all()[0]
            self.assertIs(tournament, pool.tournament)

    def test_foreign_key_multiple_prefetch(self):
        """
        Tests the prefetching of related objects using ForeignKey relationships. This function asserts that the correct number of queries are executed when fetching multiple related objects, specifically focusing on `Tournament` and `Pool` models. It uses `prefetch_related` to optimize the query and `assertIs` to verify the relationship between the fetched objects.
        
        :param None: No additional parameters are required for this function.
        :return None: The function does not return any value; it performs assertions to validate the behavior
        """

        with self.assertNumQueries(2):
            tournaments = list(
                Tournament.objects.prefetch_related("pool_set").order_by("pk")
            )
            pool1 = tournaments[0].pool_set.all()[0]
            self.assertIs(tournaments[0], pool1.tournament)
            pool2 = tournaments[1].pool_set.all()[0]
            self.assertIs(tournaments[1], pool2.tournament)

    def test_queryset_or(self):
        """
        Tests the behavior of combining querysets from two different tournaments using the OR operator.
        
        This function asserts that when combining the pool sets of two different tournaments (tournament_1 and tournament_2) using the OR operator, the resulting queryset contains pools from both tournaments. The related objects (tournaments) of the pools in the combined queryset are expected to be a set containing both tournament_1 and tournament_2.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError
        """

        tournament_1 = self.t1
        tournament_2 = self.t2
        with self.assertNumQueries(1):
            pools = tournament_1.pool_set.all() | tournament_2.pool_set.all()
            related_objects = {pool.tournament for pool in pools}
            self.assertEqual(related_objects, {tournament_1, tournament_2})

    def test_queryset_or_different_cached_items(self):
        """
        Tests querying a queryset using the OR operator with different cached items.
        
        This function asserts that a single database query is made when combining
        `tournament.pool_set.all()` and `organiser.pool_set.all()` using the OR
        operator. It then filters the resulting queryset by a specific pool's primary
        key and checks if the retrieved pool belongs to the expected tournament and
        organiser.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `
        """

        tournament = self.t1
        organiser = self.o1
        with self.assertNumQueries(1):
            pools = tournament.pool_set.all() | organiser.pool_set.all()
            first = pools.filter(pk=self.p1.pk)[0]
            self.assertIs(first.tournament, tournament)
            self.assertIs(first.organiser, organiser)

    def test_queryset_or_only_one_with_precache(self):
        """
        Tests querying pools associated with a specific tournament using `|` operator and `filter` method. Ensures that both directions of the query (tournament to pools and pools to tournament) return the correct related objects. Utilizes `assertNumQueries` to verify the number of database queries made.
        
        :param tournament_1: The first tournament object.
        :param tournament_2: The second tournament object.
        """

        tournament_1 = self.t1
        tournament_2 = self.t2
        # 2 queries here as pool 3 has tournament 2, which is not cached
        with self.assertNumQueries(2):
            pools = tournament_1.pool_set.all() | Pool.objects.filter(pk=self.p3.pk)
            related_objects = {pool.tournament for pool in pools}
            self.assertEqual(related_objects, {tournament_1, tournament_2})
        # and the other direction
        with self.assertNumQueries(2):
            pools = Pool.objects.filter(pk=self.p3.pk) | tournament_1.pool_set.all()
            related_objects = {pool.tournament for pool in pools}
            self.assertEqual(related_objects, {tournament_1, tournament_2})

    def test_queryset_and(self):
        """
        Tests the intersection of pool sets from a tournament and an organiser using the `&` operator. Ensures that the resulting pool belongs to both the specified tournament and organiser.
        
        :param tournament: The tournament object.
        :type tournament: Tournament
        :param organiser: The organiser object.
        :type organiser: Organiser
        :raises AssertionError: If the resulting pool does not belong to both the specified tournament and organiser.
        """

        tournament = self.t1
        organiser = self.o1
        with self.assertNumQueries(1):
            pools = tournament.pool_set.all() & organiser.pool_set.all()
            first = pools.filter(pk=self.p1.pk)[0]
            self.assertIs(first.tournament, tournament)
            self.assertIs(first.organiser, organiser)

    def test_one_to_one(self):
        """
        Tests the one-to-one relationship between PoolStyle and Pool models.
        
        This function asserts that a single database query is made when retrieving
        a PoolStyle instance and its associated Pool instance. It also verifies
        that the retrieved PoolStyle instance is the same as the pool's
        poolstyle attribute.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `assertNumQueries`: Asserts the number of database queries executed.
        - `get`: Retrieves
        """

        with self.assertNumQueries(2):
            style = PoolStyle.objects.get(pk=self.ps1.pk)
            pool = style.pool
            self.assertIs(style, pool.poolstyle)

    def test_one_to_one_select_related(self):
        """
        Tests one-to-one relationship with select_related.
        
        This function asserts that a single query is executed when retrieving a `PoolStyle` object and its related `Pool` object using `select_related`. It verifies that the retrieved `style` object is the same as the `poolstyle` attribute of the `pool` object.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the number of queries does not match the expected value or if the `style`
        """

        with self.assertNumQueries(1):
            style = PoolStyle.objects.select_related("pool").get(pk=self.ps1.pk)
            pool = style.pool
            self.assertIs(style, pool.poolstyle)

    def test_one_to_one_multi_select_related(self):
        """
        Tests one-to-one multi-select-related functionality.
        
        This function ensures that when querying PoolStyle objects with select_related("pool"),
        the related Pool objects are fetched in a single query, and verifies that each PoolStyle
        object correctly references its associated Pool object.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the PoolStyle objects do not correctly reference their associated Pool objects.
        
        Important Functions:
        - `PoolStyle.objects.select_related("pool
        """

        with self.assertNumQueries(1):
            poolstyles = list(PoolStyle.objects.select_related("pool").order_by("pk"))
            self.assertIs(poolstyles[0], poolstyles[0].pool.poolstyle)
            self.assertIs(poolstyles[1], poolstyles[1].pool.poolstyle)

    def test_one_to_one_prefetch_related(self):
        """
        Retrieve a PoolStyle object with its associated Pool using prefetch_related, ensuring one-to-one relationship integrity.
        
        This method fetches a PoolStyle instance along with its related Pool using `prefetch_related`. It then asserts that the fetched Pool instance has the correct PoolStyle reference.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the Pool does not have the correct PoolStyle reference.
        
        Important Functions:
        - `prefetch_related`: Fetches related objects
        """

        with self.assertNumQueries(2):
            style = PoolStyle.objects.prefetch_related("pool").get(pk=self.ps1.pk)
            pool = style.pool
            self.assertIs(style, pool.poolstyle)

    def test_one_to_one_multi_prefetch_related(self):
        """
        Tests one-to-one relationship with multiple prefetch_related queries.
        
        This function ensures that prefetching related objects using `prefetch_related` works correctly
        for a one-to-one relationship. It verifies that the related object is fetched only once, even
        when accessed multiple times within the same query set.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the related object is not fetched correctly or if the order of objects
        does not match the expected
        """

        with self.assertNumQueries(2):
            poolstyles = list(PoolStyle.objects.prefetch_related("pool").order_by("pk"))
            self.assertIs(poolstyles[0], poolstyles[0].pool.poolstyle)
            self.assertIs(poolstyles[1], poolstyles[1].pool.poolstyle)

    def test_reverse_one_to_one(self):
        """
        Tests the reverse one-to-one relationship between Pool and PoolStyle models.
        
        This function asserts that retrieving a Pool object and its associated PoolStyle
        using a reverse one-to-one relationship requires exactly two database queries.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the number of database queries does not match the expected value or if the reverse relationship is not correctly established.
        
        Important Functions:
        - `Pool.objects.get(pk=self.p2.pk)`:
        """

        with self.assertNumQueries(2):
            pool = Pool.objects.get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_select_related(self):
        """
        Tests the reverse one-to-one relationship using `select_related` with a single query.
        
        This function asserts that fetching a `Pool` object with its related `PoolStyle` using `select_related` results in only one database query and verifies that the reverse relationship is correctly established.
        
        :param self: The current test case instance.
        :type self: unittest.TestCase
        :raises AssertionError: If the number of queries does not match the expected value or if the reverse relationship is not correctly set
        """

        with self.assertNumQueries(1):
            pool = Pool.objects.select_related("poolstyle").get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_prefetch_related(self):
        """
        Tests the reverse one-to-one relationship using `prefetch_related`. This function queries the database twice to fetch the `Pool` object and its related `PoolStyle` object, ensuring that the prefetching mechanism works correctly. The function asserts that the fetched `Pool` object is the same as the related `PoolStyle` object's pool attribute.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the `Pool` object is not the same as the related
        """

        with self.assertNumQueries(2):
            pool = Pool.objects.prefetch_related("poolstyle").get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_multi_select_related(self):
        """
        Tests the reverse one-to-one relationship using multi-select-related query.
        
        This function ensures that the reverse one-to-one relationship is correctly established
        by querying the Pool model with select_related and order_by. It asserts that the pool
        object is the same when accessed through the poolstyle attribute of another pool object.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the assertion fails.
        
        Important Functions:
        - `Pool.objects.select_related("pool
        """

        with self.assertNumQueries(1):
            pools = list(Pool.objects.select_related("poolstyle").order_by("pk"))
            self.assertIs(pools[1], pools[1].poolstyle.pool)
            self.assertIs(pools[2], pools[2].poolstyle.pool)

    def test_reverse_one_to_one_multi_prefetch_related(self):
        """
        Tests the reverse one-to-one relationship using prefetch_related. This function queries the Pool model, prefetches related PoolStyle objects, orders the results by primary key, and checks if the reverse relationship is correctly established.
        
        :raises AssertionError: If the reverse relationship check fails.
        """

        with self.assertNumQueries(2):
            pools = list(Pool.objects.prefetch_related("poolstyle").order_by("pk"))
            self.assertIs(pools[1], pools[1].poolstyle.pool)
            self.assertIs(pools[2], pools[2].poolstyle.pool)

    def test_reverse_fk_select_related_multiple(self):
        """
        Tests reverse foreign key selection with multiple `select_related` usages.
        
        This function asserts that the queries are optimized to a single query using `FilteredRelation` and `select_related`. It checks if the reverse foreign key relationships are correctly selected and annotated.
        
        :param None: No additional parameters are required.
        :return: None
        """

        with self.assertNumQueries(1):
            ps = list(
                PoolStyle.objects.annotate(
                    pool_1=FilteredRelation("pool"),
                    pool_2=FilteredRelation("another_pool"),
                )
                .select_related("pool_1", "pool_2")
                .order_by("-pk")
            )
            self.assertIs(ps[0], ps[0].pool_1.poolstyle)
            self.assertIs(ps[0], ps[0].pool_2.another_style)
