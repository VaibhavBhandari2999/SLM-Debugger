from django.test import TestCase

from .models import Organiser, Pool, PoolStyle, Tournament


class ExistingRelatedInstancesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for tournament-related tests.
        
        This method creates a set of test data for use in tournament-related tests. It creates four tournaments, each with an organiser, and two pools per tournament. Additionally, it creates pool styles for specific pools.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Test Data Created:
        - 2 Tournaments (t1, t2)
        - 2 Organisers (o1)
        - 4 Pools (p1, p2, p
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

    def test_foreign_key(self):
        with self.assertNumQueries(2):
            tournament = Tournament.objects.get(pk=self.t1.pk)
            pool = tournament.pool_set.all()[0]
            self.assertIs(tournament, pool.tournament)

    def test_foreign_key_prefetch_related(self):
        """
        Tests the prefetch_related functionality for a ForeignKey relationship.
        
        This function ensures that when a Tournament object is fetched with its associated Pool objects prefetched, the ForeignKey relationship between the Pool and Tournament is correctly maintained.
        
        Parameters:
        - None
        
        Assertions:
        - The tournament object is the same as the one referenced by the pool's tournament ForeignKey.
        - The number of database queries is limited to 2.
        
        Usage:
        This test function is used to verify that prefetch_related works as expected for ForeignKey relationships in Django ORM.
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
        Tests the behavior of combining querysets from two different tournaments using the OR operator.
        
        This function asserts that the combined queryset of pools from two different tournaments (tournament_1 and tournament_2) contains pools from both tournaments. It ensures that the resulting queryset does not include pools from any other tournaments.
        
        Parameters:
        - tournament_1 (Tournament): The first tournament from which to retrieve pools.
        - tournament_2 (Tournament): The second tournament from which to retrieve pools.
        
        Returns:
        - None:
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
        with self.assertNumQueries(1):
            style = PoolStyle.objects.select_related("pool").get(pk=self.ps1.pk)
            pool = style.pool
            self.assertIs(style, pool.poolstyle)

    def test_one_to_one_multi_select_related(self):
        """
        Tests the one-to-one relationship with multiple select_related queries.
        
        This function ensures that a list of PoolStyle objects is fetched with their associated Pool objects in a single query. It then checks if the fetched PoolStyle objects correctly reference their associated Pool objects.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The length of the PoolStyle list is 2.
        - The first PoolStyle object in the list is the same as the one referenced by its pool attribute.
        - The
        """

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
        """
        Tests the reverse one-to-one relationship with select_related.
        
        This function ensures that a single query is used to fetch the related poolstyle
        for a given pool object. It uses `select_related` to optimize the query and
        asserts that the reverse relationship is correctly set.
        
        Parameters:
        None
        
        Assertions:
        - The number of database queries is exactly 1.
        - The pool object and its related poolstyle are correctly linked, i.e., `pool.poolstyle` is the same as
        """

        with self.assertNumQueries(1):
            pool = Pool.objects.select_related("poolstyle").get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_prefetch_related(self):
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
 self.assertIs(pools[2], pools[2].poolstyle.pool)
