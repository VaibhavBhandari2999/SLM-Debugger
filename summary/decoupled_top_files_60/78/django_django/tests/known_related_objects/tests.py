from django.test import TestCase

from .models import Organiser, Pool, PoolStyle, Tournament


class ExistingRelatedInstancesTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for tournament-related models.
        
        This method creates a set of test data for use in unit tests. It creates four tournaments, each with an associated organiser and two pools. Additionally, it sets up pool styles for specific pools.
        
        Key Parameters:
        - None (This method is a class method and is intended to be called on a class)
        
        Returns:
        - None (This method populates the database with test data)
        
        Example Usage:
        ```python
        class TestTournamentModels(TestCase):
        """

        cls.t1 = Tournament.objects.create(name='Tourney 1')
        cls.t2 = Tournament.objects.create(name='Tourney 2')
        cls.o1 = Organiser.objects.create(name='Organiser 1')
        cls.p1 = Pool.objects.create(name='T1 Pool 1', tournament=cls.t1, organiser=cls.o1)
        cls.p2 = Pool.objects.create(name='T1 Pool 2', tournament=cls.t1, organiser=cls.o1)
        cls.p3 = Pool.objects.create(name='T2 Pool 1', tournament=cls.t2, organiser=cls.o1)
        cls.p4 = Pool.objects.create(name='T2 Pool 2', tournament=cls.t2, organiser=cls.o1)
        cls.ps1 = PoolStyle.objects.create(name='T1 Pool 2 Style', pool=cls.p2)
        cls.ps2 = PoolStyle.objects.create(name='T2 Pool 1 Style', pool=cls.p3)

    def test_foreign_key(self):
        with self.assertNumQueries(2):
            tournament = Tournament.objects.get(pk=self.t1.pk)
            pool = tournament.pool_set.all()[0]
            self.assertIs(tournament, pool.tournament)

    def test_foreign_key_prefetch_related(self):
        with self.assertNumQueries(2):
            tournament = (Tournament.objects.prefetch_related('pool_set').get(pk=self.t1.pk))
            pool = tournament.pool_set.all()[0]
            self.assertIs(tournament, pool.tournament)

    def test_foreign_key_multiple_prefetch(self):
        """
        Tests the prefetch_related functionality with multiple queries for foreign key relationships.
        
        This function ensures that when prefetching related 'pool_set' objects for a list of 'Tournament' objects, the prefetching is correctly implemented and that related objects can be accessed without additional queries.
        
        Parameters:
        None
        
        Assertions:
        - The first pool in the first tournament is correctly associated with that tournament.
        - The first pool in the second tournament is correctly associated with that tournament.
        
        Query Count:
        - The function asserts
        """

        with self.assertNumQueries(2):
            tournaments = list(Tournament.objects.prefetch_related('pool_set').order_by('pk'))
            pool1 = tournaments[0].pool_set.all()[0]
            self.assertIs(tournaments[0], pool1.tournament)
            pool2 = tournaments[1].pool_set.all()[0]
            self.assertIs(tournaments[1], pool2.tournament)

    def test_queryset_or(self):
        tournament_1 = self.t1
        tournament_2 = self.t2
        with self.assertNumQueries(1):
            pools = tournament_1.pool_set.all() | tournament_2.pool_set.all()
            related_objects = {pool.tournament for pool in pools}
            self.assertEqual(related_objects, {tournament_1, tournament_2})

    def test_queryset_or_different_cached_items(self):
        """
        Tests the behavior of a queryset that combines results from two different sources (a tournament's pool_set and an organiser's pool_set) without causing additional database queries.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The first pool in the combined queryset has the correct tournament and organiser attributes.
        - The combined queryset is fetched with only one database query.
        
        Usage:
        This function is used to verify that the queryset operation `|` (union) between two different sources does
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
        Tests the behavior of the `Pool` queryset when using the `|` operator (union) with a precached object.
        
        This function checks the number of database queries made when using the `|` operator to combine two `Pool` querysets. The first queryset is the `pool_set` of `tournament_1`, and the second queryset is a `Pool` object from `tournament_2`. The function ensures that only two queries are made, even when the second queryset is not cached.
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
        Tests the one-to-one relationship and select_related functionality.
        
        This method verifies that a single database query is used to fetch the PoolStyle and its related Pool object. It asserts that the fetched PoolStyle object is the same as the Pool's poolstyle attribute.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The number of database queries is exactly 1.
        - The fetched PoolStyle object is the same as the Pool's poolstyle attribute.
        """

        with self.assertNumQueries(1):
            style = PoolStyle.objects.select_related('pool').get(pk=self.ps1.pk)
            pool = style.pool
            self.assertIs(style, pool.poolstyle)

    def test_one_to_one_multi_select_related(self):
        with self.assertNumQueries(1):
            poolstyles = list(PoolStyle.objects.select_related('pool').order_by('pk'))
            self.assertIs(poolstyles[0], poolstyles[0].pool.poolstyle)
            self.assertIs(poolstyles[1], poolstyles[1].pool.poolstyle)

    def test_one_to_one_prefetch_related(self):
        """
        Tests the one-to-one relationship with prefetch_related.
        
        This function asserts that fetching a PoolStyle object with its related pool using prefetch_related results in exactly two database queries. The function retrieves the PoolStyle object with the specified primary key and then accesses its related pool. It ensures that the pool's poolstyle attribute points back to the original PoolStyle object.
        
        Parameters:
        None
        
        Assertions:
        - The number of database queries is exactly 2.
        - The pool's poolstyle attribute is the same
        """

        with self.assertNumQueries(2):
            style = PoolStyle.objects.prefetch_related('pool').get(pk=self.ps1.pk)
            pool = style.pool
            self.assertIs(style, pool.poolstyle)

    def test_one_to_one_multi_prefetch_related(self):
        with self.assertNumQueries(2):
            poolstyles = list(PoolStyle.objects.prefetch_related('pool').order_by('pk'))
            self.assertIs(poolstyles[0], poolstyles[0].pool.poolstyle)
            self.assertIs(poolstyles[1], poolstyles[1].pool.poolstyle)

    def test_reverse_one_to_one(self):
        with self.assertNumQueries(2):
            pool = Pool.objects.get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_select_related(self):
        with self.assertNumQueries(1):
            pool = Pool.objects.select_related('poolstyle').get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_prefetch_related(self):
        with self.assertNumQueries(2):
            pool = Pool.objects.prefetch_related('poolstyle').get(pk=self.p2.pk)
            style = pool.poolstyle
            self.assertIs(pool, style.pool)

    def test_reverse_one_to_one_multi_select_related(self):
        """
        Tests the reverse one-to-one relationship with multiple select-related queries.
        
        This function ensures that a list of Pool objects is fetched with their associated PoolStyle objects in a single query. It then checks that the reverse relationship is correctly established.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The length of the pools list is at least 2.
        - The pool referenced by the poolstyle of the second pool object is the same as the second pool object.
        - The pool referenced
        """

        with self.assertNumQueries(1):
            pools = list(Pool.objects.select_related('poolstyle').order_by('pk'))
            self.assertIs(pools[1], pools[1].poolstyle.pool)
            self.assertIs(pools[2], pools[2].poolstyle.pool)

    def test_reverse_one_to_one_multi_prefetch_related(self):
        with self.assertNumQueries(2):
            pools = list(Pool.objects.prefetch_related('poolstyle').order_by('pk'))
            self.assertIs(pools[1], pools[1].poolstyle.pool)
            self.assertIs(pools[2], pools[2].poolstyle.pool)
.pool)
