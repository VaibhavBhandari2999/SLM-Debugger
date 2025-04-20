from django.db.models import FilteredRelation
from django.test import TestCase

from .models import Organiser, Pool, PoolStyle, Tournament


class ExistingRelatedInstancesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for tournament-related tests.
        
        This method creates a set of test data for use in tournament-related tests. It creates four tournaments, each with an associated organiser. For each tournament, it creates two pools, and for some pools, it assigns a pool style.
        
        Key Parameters:
        - None (This is a class method, so no individual parameters are passed to it directly)
        
        Output:
        - A set of test data consisting of:
        - Two tournaments (`cls.t1`, `cls
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
        with self.assertNumQueries(2):
            tournament = Tournament.objects.get(pk=self.t1.pk)
            pool = tournament.pool_set.all()[0]
            self.assertIs(tournament, pool.tournament)

    def test_foreign_key_prefetch_related(self):
        """
        Tests the prefetch_related functionality for foreign key relationships in the Tournament model.
        
        This method ensures that when a Tournament object is fetched with its associated pool_set prefetched, the related pool objects correctly reference their tournament.
        
        Parameters:
        None
        
        Assertions:
        - The fetched tournament and its first pool's tournament reference should be the same.
        
        Query Count:
        - The method asserts that exactly 2 queries are executed: one for fetching the tournament with its pools and one for retrieving the first pool.
        
        Usage:
        """

        with self.assertNumQueries(2):
            tournament = Tournament.objects.prefetch_related("pool_set").get(
                pk=self.t1.pk
            )
            pool = tournament.pool_set.all()[0]
            self.assertIs(tournament, pool.tournament)

    def test_foreign_key_multiple_prefetch(self):
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
        Tests the behavior of a queryset union operation across two different tournaments.
        
        This function asserts that the union of pool sets from two different tournaments returns a combined set of pools without duplicates, and that each pool is correctly associated with its respective tournament.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The union of pool sets from `tournament_1` and `tournament_2` should contain pools from both tournaments without duplicates.
        - Each pool in the union should be correctly associated with its
        """

        tournament_1 = self.t1
        tournament_2 = self.t2
        with self.assertNumQueries(1):
            pools = tournament_1.pool_set.all() | tournament_2.pool_set.all()
            related_objects = {pool.tournament for pool in pools}
            self.assertEqual(related_objects, {tournament_1, tournament_2})

    def test_queryset_or_different_cached_items(self):
        tournament = self.t1
        organiser = self.o1
        with self.assertNumQueries(1):
            pools = tournament.pool_set.all() | organiser.pool_set.all()
            first = pools.filter(pk=self.p1.pk)[0]
            self.assertIs(first.tournament, tournament)
            self.assertIs(first.organiser, organiser)

    def test_queryset_or_only_one_with_precache(self):
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
        tournament = self.t1
        organiser = self.o1
        with self.assertNumQueries(1):
            pools = tournament.pool_set.all() & organiser.pool_set.all()
            first = pools.filter(pk=self.p1.pk)[0]
            self.assertIs(first.tournament, tournament)
            self.assertIs(first.organiser, organiser)

    def test_one_to_one(self):
        with self.assertNumQueries(2):
            style = PoolStyle.objects.get(pk=self.ps1.pk)
            pool = style.pool
            self.assertIs(style, pool.poolstyle)

    def test_one_to_one_select_related(self):
        """
        Tests the one-to-one select_related functionality.
        
        This function verifies that a single query is used to fetch a PoolStyle object and its related Pool object. The PoolStyle object is retrieved using select_related, which optimizes the query by joining the related tables.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The number of queries executed is exactly 1.
        - The retrieved PoolStyle object is the same as the related Pool object's poolstyle attribute.
        """

        with self.assertNumQueries(1):
            style = PoolStyle.objects.select_related("pool").get(pk=self.ps1.pk)
            pool = style.pool
            self.assertIs(style, pool.poolstyle)

    def test_one_to_one_multi_select_related(self):
        with self.assertNumQueries(1):
            poolstyles = list(PoolStyle.objects.select_related("pool").order_by("pk"))
            self.assertIs(poolstyles[0], poolstyles[0].pool.poolstyle)
            self.assertIs(poolstyles[1], poolstyles[1].pool.poolstyle)

    def test_one_to_one_prefetch_related(self):
        with self.assertNumQueries(2):
            style = PoolStyle.objects.prefetch_related("pool").get(pk=self.ps1.pk)
            pool = style.pool
            self.assertIs(style, pool.poolstyle)

    def test_one_to_one_multi_prefetch_related(self):
        with self.assertNumQueries(2):
            poolstyles = list(PoolStyle.objects.prefetch_related("pool").order_by("pk"))
            self.assertIs(poolstyles[0], poolstyles[0].pool.poolstyle)
            self.assertIs(poolstyles[1], poolstyles[1].pool.poolstyle)

    def test_reverse_one_to_one(self):
        with self.assertNumQueries(2):
            pool = Pool.objects.get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_select_related(self):
        with self.assertNumQueries(1):
            pool = Pool.objects.select_related("poolstyle").get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_prefetch_related(self):
        """
        Tests the reverse one-to-one relationship using `prefetch_related`.
        
        This function ensures that the reverse one-to-one relationship between Pool and PoolStyle is correctly handled when using `prefetch_related`. It expects a single database query to fetch the related PoolStyle object.
        
        Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - No external input is required. The function uses an existing pool object (self.p2).
        
        Output:
        - The function asserts that the fetched Pool object and the related PoolStyle object
        """

        with self.assertNumQueries(2):
            pool = Pool.objects.prefetch_related("poolstyle").get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_multi_select_related(self):
        with self.assertNumQueries(1):
            pools = list(Pool.objects.select_related("poolstyle").order_by("pk"))
            self.assertIs(pools[1], pools[1].poolstyle.pool)
            self.assertIs(pools[2], pools[2].poolstyle.pool)

    def test_reverse_one_to_one_multi_prefetch_related(self):
        with self.assertNumQueries(2):
            pools = list(Pool.objects.prefetch_related("poolstyle").order_by("pk"))
            self.assertIs(pools[1], pools[1].poolstyle.pool)
            self.assertIs(pools[2], pools[2].poolstyle.pool)

    def test_reverse_fk_select_related_multiple(self):
        """
        Tests the reverse foreign key select related functionality with multiple related objects.
        
        This function asserts that the queries are optimized to a single query and that the reverse foreign key relationships are correctly selected and related.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The number of queries executed is exactly 1.
        - The first PoolStyle object in the list is the same as its related pool_1 and pool_2 objects.
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
