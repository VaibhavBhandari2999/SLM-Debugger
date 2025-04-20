import operator

from django.db import DatabaseError, NotSupportedError, connection
from django.db.models import Exists, F, IntegerField, OuterRef, Value
from django.test import TestCase, skipIfDBFeature, skipUnlessDBFeature
from django.test.utils import CaptureQueriesContext

from .models import Number, ReservedName


@skipUnlessDBFeature('supports_select_union')
class QuerySetSetOperationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Number.objects.bulk_create(Number(num=i, other_num=10 - i) for i in range(10))

    def assertNumbersEqual(self, queryset, expected_numbers, ordered=True):
        self.assertQuerysetEqual(queryset, expected_numbers, operator.attrgetter('num'), ordered)

    def test_simple_union(self):
        """
        Tests the union operation on querysets.
        
        This function checks the union operation on three different querysets:
        - `qs1`: Numbers less than or equal to 1.
        - `qs2`: Numbers greater than or equal to 8.
        - `qs3`: The number 5.
        
        The expected result is a combined queryset of numbers [0, 1, 5, 8, 9] in any order.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        -
        """

        qs1 = Number.objects.filter(num__lte=1)
        qs2 = Number.objects.filter(num__gte=8)
        qs3 = Number.objects.filter(num=5)
        self.assertNumbersEqual(qs1.union(qs2, qs3), [0, 1, 5, 8, 9], ordered=False)

    @skipUnlessDBFeature('supports_select_intersection')
    def test_simple_intersection(self):
        qs1 = Number.objects.filter(num__lte=5)
        qs2 = Number.objects.filter(num__gte=5)
        qs3 = Number.objects.filter(num__gte=4, num__lte=6)
        self.assertNumbersEqual(qs1.intersection(qs2, qs3), [5], ordered=False)

    @skipUnlessDBFeature('supports_select_intersection')
    def test_intersection_with_values(self):
        ReservedName.objects.create(name='a', order=2)
        qs1 = ReservedName.objects.all()
        reserved_name = qs1.intersection(qs1).values('name', 'order', 'id').get()
        self.assertEqual(reserved_name['name'], 'a')
        self.assertEqual(reserved_name['order'], 2)
        reserved_name = qs1.intersection(qs1).values_list('name', 'order', 'id').get()
        self.assertEqual(reserved_name[:2], ('a', 2))

    @skipUnlessDBFeature('supports_select_difference')
    def test_simple_difference(self):
        qs1 = Number.objects.filter(num__lte=5)
        qs2 = Number.objects.filter(num__lte=4)
        self.assertNumbersEqual(qs1.difference(qs2), [5], ordered=False)

    def test_union_distinct(self):
        qs1 = Number.objects.all()
        qs2 = Number.objects.all()
        self.assertEqual(len(list(qs1.union(qs2, all=True))), 20)
        self.assertEqual(len(list(qs1.union(qs2))), 10)

    def test_union_none(self):
        qs1 = Number.objects.filter(num__lte=1)
        qs2 = Number.objects.filter(num__gte=8)
        qs3 = qs1.union(qs2)
        self.assertSequenceEqual(qs3.none(), [])
        self.assertNumbersEqual(qs3, [0, 1, 8, 9], ordered=False)

    @skipUnlessDBFeature('supports_select_intersection')
    def test_intersection_with_empty_qs(self):
        """
        Tests the intersection method of QuerySets with empty QuerySets.
        
        This function tests the intersection method of Django's QuerySet objects when one or both of the QuerySets are empty. It checks the length of the intersection for various combinations of empty and non-empty QuerySets.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - `qs1`: A non-empty QuerySet containing all objects of the Number model.
        - `qs2`: An empty QuerySet.
        - `qs3`: An
        """

        qs1 = Number.objects.all()
        qs2 = Number.objects.none()
        qs3 = Number.objects.filter(pk__in=[])
        self.assertEqual(len(qs1.intersection(qs2)), 0)
        self.assertEqual(len(qs1.intersection(qs3)), 0)
        self.assertEqual(len(qs2.intersection(qs1)), 0)
        self.assertEqual(len(qs3.intersection(qs1)), 0)
        self.assertEqual(len(qs2.intersection(qs2)), 0)
        self.assertEqual(len(qs3.intersection(qs3)), 0)

    @skipUnlessDBFeature('supports_select_difference')
    def test_difference_with_empty_qs(self):
        """
        Test the difference method of QuerySet objects.
        
        This function tests the difference method of Django's QuerySet objects with various scenarios. The method returns a new QuerySet containing elements that are in the first QuerySet but not in the second one.
        
        Parameters:
        - qs1 (QuerySet): The first QuerySet, which contains 10 elements.
        - qs2 (QuerySet): The second QuerySet, which is empty (contains no elements).
        - qs3 (QuerySet): The third QuerySet
        """

        qs1 = Number.objects.all()
        qs2 = Number.objects.none()
        qs3 = Number.objects.filter(pk__in=[])
        self.assertEqual(len(qs1.difference(qs2)), 10)
        self.assertEqual(len(qs1.difference(qs3)), 10)
        self.assertEqual(len(qs2.difference(qs1)), 0)
        self.assertEqual(len(qs3.difference(qs1)), 0)
        self.assertEqual(len(qs2.difference(qs2)), 0)
        self.assertEqual(len(qs3.difference(qs3)), 0)

    @skipUnlessDBFeature('supports_select_difference')
    def test_difference_with_values(self):
        ReservedName.objects.create(name='a', order=2)
        qs1 = ReservedName.objects.all()
        qs2 = ReservedName.objects.none()
        reserved_name = qs1.difference(qs2).values('name', 'order', 'id').get()
        self.assertEqual(reserved_name['name'], 'a')
        self.assertEqual(reserved_name['order'], 2)
        reserved_name = qs1.difference(qs2).values_list('name', 'order', 'id').get()
        self.assertEqual(reserved_name[:2], ('a', 2))

    def test_union_with_empty_qs(self):
        qs1 = Number.objects.all()
        qs2 = Number.objects.none()
        qs3 = Number.objects.filter(pk__in=[])
        self.assertEqual(len(qs1.union(qs2)), 10)
        self.assertEqual(len(qs2.union(qs1)), 10)
        self.assertEqual(len(qs1.union(qs3)), 10)
        self.assertEqual(len(qs3.union(qs1)), 10)
        self.assertEqual(len(qs2.union(qs1, qs1, qs1)), 10)
        self.assertEqual(len(qs2.union(qs1, qs1, all=True)), 20)
        self.assertEqual(len(qs2.union(qs2)), 0)
        self.assertEqual(len(qs3.union(qs3)), 0)

    def test_empty_qs_union_with_ordered_qs(self):
        qs1 = Number.objects.all().order_by('num')
        qs2 = Number.objects.none().union(qs1).order_by('num')
        self.assertEqual(list(qs1), list(qs2))

    def test_limits(self):
        """
        Tests the union operation of two querysets.
        
        This function compares the length of the first two elements in the union of two querysets (qs1 and qs2) to ensure that the result contains exactly two elements.
        
        Parameters:
        self: The test case instance (unittest.TestCase).
        
        Returns:
        None. This function asserts the result and does not return any value.
        
        Key Parameters:
        qs1: The first queryset of Number objects.
        qs2: The second queryset of Number objects.
        
        Keywords:
        """

        qs1 = Number.objects.all()
        qs2 = Number.objects.all()
        self.assertEqual(len(list(qs1.union(qs2)[:2])), 2)

    def test_ordering(self):
        """
        Tests the ordering of a union of two querysets.
        
        Args:
        self: The test case instance.
        
        Parameters:
        qs1 (QuerySet): A queryset filtering numbers less than or equal to 1.
        qs2 (QuerySet): A queryset filtering numbers greater than or equal to 2 and less than or equal to 3.
        
        Returns:
        None: The function asserts the equality of the ordered union of the two querysets against a predefined list of numbers.
        """

        qs1 = Number.objects.filter(num__lte=1)
        qs2 = Number.objects.filter(num__gte=2, num__lte=3)
        self.assertNumbersEqual(qs1.union(qs2).order_by('-num'), [3, 2, 1, 0])

    def test_ordering_by_alias(self):
        qs1 = Number.objects.filter(num__lte=1).values(alias=F('num'))
        qs2 = Number.objects.filter(num__gte=2, num__lte=3).values(alias=F('num'))
        self.assertQuerysetEqual(
            qs1.union(qs2).order_by('-alias'),
            [3, 2, 1, 0],
            operator.itemgetter('alias'),
        )

    def test_ordering_by_f_expression(self):
        """
        Tests the ordering of a queryset using an F expression.
        
        This function checks the ordering of a queryset that combines two subqueries using the `union` method and orders the result in descending order based on the 'num' field using an F expression.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - `qs1`: A queryset filtering numbers less than or equal to 1.
        - `qs2`: A queryset filtering numbers greater than or equal to 2 and less than
        """

        qs1 = Number.objects.filter(num__lte=1)
        qs2 = Number.objects.filter(num__gte=2, num__lte=3)
        self.assertNumbersEqual(qs1.union(qs2).order_by(F('num').desc()), [3, 2, 1, 0])

    def test_ordering_by_f_expression_and_alias(self):
        """
        Tests the ordering of a queryset using F expressions and aliases.
        
        This function tests the ordering of a queryset that contains values derived from F expressions and aliases. It creates two separate querysets, `qs1` and `qs2`, based on different conditions and then combines them using the `union` method. The combined queryset is then ordered by the alias, which is derived from the `other_num` field, in descending order. The function asserts that the resulting queryset is ordered correctly.
        
        Parameters:
        -
        """

        qs1 = Number.objects.filter(num__lte=1).values(alias=F('other_num'))
        qs2 = Number.objects.filter(num__gte=2, num__lte=3).values(alias=F('other_num'))
        self.assertQuerysetEqual(
            qs1.union(qs2).order_by(F('alias').desc()),
            [10, 9, 8, 7],
            operator.itemgetter('alias'),
        )
        Number.objects.create(num=-1)
        self.assertQuerysetEqual(
            qs1.union(qs2).order_by(F('alias').desc(nulls_last=True)),
            [10, 9, 8, 7, None],
            operator.itemgetter('alias'),
        )

    def test_union_with_values(self):
        ReservedName.objects.create(name='a', order=2)
        qs1 = ReservedName.objects.all()
        reserved_name = qs1.union(qs1).values('name', 'order', 'id').get()
        self.assertEqual(reserved_name['name'], 'a')
        self.assertEqual(reserved_name['order'], 2)
        reserved_name = qs1.union(qs1).values_list('name', 'order', 'id').get()
        self.assertEqual(reserved_name[:2], ('a', 2))
        # List of columns can be changed.
        reserved_name = qs1.union(qs1).values_list('order').get()
        self.assertEqual(reserved_name, (2,))

    def test_union_with_two_annotated_values_list(self):
        qs1 = Number.objects.filter(num=1).annotate(
            count=Value(0, IntegerField()),
        ).values_list('num', 'count')
        qs2 = Number.objects.filter(num=2).values('pk').annotate(
            count=F('num'),
        ).annotate(
            num=Value(1, IntegerField()),
        ).values_list('num', 'count')
        self.assertCountEqual(qs1.union(qs2), [(1, 0), (2, 1)])

    def test_union_with_extra_and_values_list(self):
        """
        Test the union operation on two querysets with extra and values_list.
        
        Parameters:
        - qs1 (QuerySet): The first queryset, filtered for num=1 and with an extra select clause to include a count of 0.
        - qs2 (QuerySet): The second queryset, filtered for num=2 and with an extra select clause to include a count of 1.
        
        Returns:
        - A list of tuples, each containing a number and its corresponding count, as returned by the union operation
        """

        qs1 = Number.objects.filter(num=1).extra(
            select={'count': 0},
        ).values_list('num', 'count')
        qs2 = Number.objects.filter(num=2).extra(select={'count': 1})
        self.assertCountEqual(qs1.union(qs2), [(1, 0), (2, 1)])

    def test_union_with_values_list_on_annotated_and_unannotated(self):
        ReservedName.objects.create(name='rn1', order=1)
        qs1 = Number.objects.annotate(
            has_reserved_name=Exists(ReservedName.objects.filter(order=OuterRef('num')))
        ).filter(has_reserved_name=True)
        qs2 = Number.objects.filter(num=9)
        self.assertCountEqual(qs1.union(qs2).values_list('num', flat=True), [1, 9])

    def test_union_with_values_list_and_order(self):
        ReservedName.objects.bulk_create([
            ReservedName(name='rn1', order=7),
            ReservedName(name='rn2', order=5),
            ReservedName(name='rn0', order=6),
            ReservedName(name='rn9', order=-1),
        ])
        qs1 = ReservedName.objects.filter(order__gte=6)
        qs2 = ReservedName.objects.filter(order__lte=5)
        union_qs = qs1.union(qs2)
        for qs, expected_result in (
            # Order by a single column.
            (union_qs.order_by('-pk').values_list('order', flat=True), [-1, 6, 5, 7]),
            (union_qs.order_by('pk').values_list('order', flat=True), [7, 5, 6, -1]),
            (union_qs.values_list('order', flat=True).order_by('-pk'), [-1, 6, 5, 7]),
            (union_qs.values_list('order', flat=True).order_by('pk'), [7, 5, 6, -1]),
            # Order by multiple columns.
            (union_qs.order_by('-name', 'pk').values_list('order', flat=True), [-1, 5, 7, 6]),
            (union_qs.values_list('order', flat=True).order_by('-name', 'pk'), [-1, 5, 7, 6]),
        ):
            with self.subTest(qs=qs):
                self.assertEqual(list(qs), expected_result)

    def test_union_with_values_list_and_order_on_annotation(self):
        """
        Tests the union operation with values list and order by annotation.
        
        This test function checks the behavior of the `union` method on two querysets. Each queryset is annotated with a constant value and a multiplier, then filtered based on the `num` field. The resulting union of these two querysets is then ordered and the values of the 'num' field are compared against a predefined list.
        
        Parameters:
        - `qs1`: The first queryset, annotated with a constant value of -1 and a multiplier
        """

        qs1 = Number.objects.annotate(
            annotation=Value(-1),
            multiplier=F('annotation'),
        ).filter(num__gte=6)
        qs2 = Number.objects.annotate(
            annotation=Value(2),
            multiplier=F('annotation'),
        ).filter(num__lte=5)
        self.assertSequenceEqual(
            qs1.union(qs2).order_by('annotation', 'num').values_list('num', flat=True),
            [6, 7, 8, 9, 0, 1, 2, 3, 4, 5],
        )
        self.assertQuerysetEqual(
            qs1.union(qs2).order_by(
                F('annotation') * F('multiplier'),
                'num',
            ).values('num'),
            [6, 7, 8, 9, 0, 1, 2, 3, 4, 5],
            operator.itemgetter('num'),
        )

    def test_count_union(self):
        qs1 = Number.objects.filter(num__lte=1).values('num')
        qs2 = Number.objects.filter(num__gte=2, num__lte=3).values('num')
        self.assertEqual(qs1.union(qs2).count(), 4)

    def test_count_union_empty_result(self):
        qs = Number.objects.filter(pk__in=[])
        self.assertEqual(qs.union(qs).count(), 0)

    @skipUnlessDBFeature('supports_select_difference')
    def test_count_difference(self):
        """
        Test the count_difference method of a QuerySet.
        
        Parameters:
        - self: The test case instance (unittest.TestCase).
        
        This method filters two QuerySets, `qs1` and `qs2`, based on the number field. `qs1` filters numbers less than 10, while `qs2` filters numbers less than 9. It then calculates the difference between these two QuerySets and asserts that the count of the resulting QuerySet is 1.
        """

        qs1 = Number.objects.filter(num__lt=10)
        qs2 = Number.objects.filter(num__lt=9)
        self.assertEqual(qs1.difference(qs2).count(), 1)

    @skipUnlessDBFeature('supports_select_intersection')
    def test_count_intersection(self):
        qs1 = Number.objects.filter(num__gte=5)
        qs2 = Number.objects.filter(num__lte=5)
        self.assertEqual(qs1.intersection(qs2).count(), 1)

    def test_exists_union(self):
        """
        Tests the `exists` method of the `union` query operation.
        
        This function checks if the `exists` method returns `True` when used with the `union` method on two querysets. The first queryset (`qs1`) filters numbers greater than or equal to 5, while the second queryset (`qs2`) filters numbers less than or equal to 5. The test captures the database queries executed during this operation and ensures that only one query is made. Additionally, it verifies that the
        """

        qs1 = Number.objects.filter(num__gte=5)
        qs2 = Number.objects.filter(num__lte=5)
        with CaptureQueriesContext(connection) as context:
            self.assertIs(qs1.union(qs2).exists(), True)
        captured_queries = context.captured_queries
        self.assertEqual(len(captured_queries), 1)
        captured_sql = captured_queries[0]['sql']
        self.assertNotIn(
            connection.ops.quote_name(Number._meta.pk.column),
            captured_sql,
        )
        self.assertEqual(
            captured_sql.count(connection.ops.limit_offset_sql(None, 1)),
            3 if connection.features.supports_slicing_ordering_in_compound else 1
        )

    def test_exists_union_empty_result(self):
        qs = Number.objects.filter(pk__in=[])
        self.assertIs(qs.union(qs).exists(), False)

    @skipUnlessDBFeature('supports_select_intersection')
    def test_exists_intersection(self):
        qs1 = Number.objects.filter(num__gt=5)
        qs2 = Number.objects.filter(num__lt=5)
        self.assertIs(qs1.intersection(qs1).exists(), True)
        self.assertIs(qs1.intersection(qs2).exists(), False)

    @skipUnlessDBFeature('supports_select_difference')
    def test_exists_difference(self):
        qs1 = Number.objects.filter(num__gte=5)
        qs2 = Number.objects.filter(num__gte=3)
        self.assertIs(qs1.difference(qs2).exists(), False)
        self.assertIs(qs2.difference(qs1).exists(), True)

    def test_get_union(self):
        qs = Number.objects.filter(num=2)
        self.assertEqual(qs.union(qs).get().num, 2)

    @skipUnlessDBFeature('supports_select_difference')
    def test_get_difference(self):
        qs1 = Number.objects.all()
        qs2 = Number.objects.exclude(num=2)
        self.assertEqual(qs1.difference(qs2).get().num, 2)

    @skipUnlessDBFeature('supports_select_intersection')
    def test_get_intersection(self):
        qs1 = Number.objects.all()
        qs2 = Number.objects.filter(num=2)
        self.assertEqual(qs1.intersection(qs2).get().num, 2)

    @skipUnlessDBFeature('supports_slicing_ordering_in_compound')
    def test_ordering_subqueries(self):
        qs1 = Number.objects.order_by('num')[:2]
        qs2 = Number.objects.order_by('-num')[:2]
        self.assertNumbersEqual(qs1.union(qs2).order_by('-num')[:4], [9, 8, 1, 0])

    @skipIfDBFeature('supports_slicing_ordering_in_compound')
    def test_unsupported_ordering_slicing_raises_db_error(self):
        qs1 = Number.objects.all()
        qs2 = Number.objects.all()
        qs3 = Number.objects.all()
        msg = 'LIMIT/OFFSET not allowed in subqueries of compound statements'
        with self.assertRaisesMessage(DatabaseError, msg):
            list(qs1.union(qs2[:10]))
        msg = 'ORDER BY not allowed in subqueries of compound statements'
        with self.assertRaisesMessage(DatabaseError, msg):
            list(qs1.order_by('id').union(qs2))
        with self.assertRaisesMessage(DatabaseError, msg):
            list(qs1.union(qs2).order_by('id').union(qs3))

    @skipIfDBFeature('supports_select_intersection')
    def test_unsupported_intersection_raises_db_error(self):
        qs1 = Number.objects.all()
        qs2 = Number.objects.all()
        msg = 'intersection is not supported on this database backend'
        with self.assertRaisesMessage(NotSupportedError, msg):
            list(qs1.intersection(qs2))

    def test_combining_multiple_models(self):
        ReservedName.objects.create(name='99 little bugs', order=99)
        qs1 = Number.objects.filter(num=1).values_list('num', flat=True)
        qs2 = ReservedName.objects.values_list('order')
        self.assertEqual(list(qs1.union(qs2).order_by('num')), [1, 99])

    def test_order_raises_on_non_selected_column(self):
        qs1 = Number.objects.filter().annotate(
            annotation=Value(1, IntegerField()),
        ).values('annotation', num2=F('num'))
        qs2 = Number.objects.filter().values('id', 'num')
        # Should not raise
        list(qs1.union(qs2).order_by('annotation'))
        list(qs1.union(qs2).order_by('num2'))
        msg = 'ORDER BY term does not match any column in the result set'
        # 'id' is not part of the select
        with self.assertRaisesMessage(DatabaseError, msg):
            list(qs1.union(qs2).order_by('id'))
        # 'num' got realiased to num2
        with self.assertRaisesMessage(DatabaseError, msg):
            list(qs1.union(qs2).order_by('num'))
        with self.assertRaisesMessage(DatabaseError, msg):
            list(qs1.union(qs2).order_by(F('num')))
        with self.assertRaisesMessage(DatabaseError, msg):
            list(qs1.union(qs2).order_by(F('num').desc()))
        # switched order, now 'exists' again:
        list(qs2.union(qs1).order_by('num'))

    @skipUnlessDBFeature('supports_select_difference', 'supports_select_intersection')
    def test_qs_with_subcompound_qs(self):
        qs1 = Number.objects.all()
        qs2 = Number.objects.intersection(Number.objects.filter(num__gt=1))
        self.assertEqual(qs1.difference(qs2).count(), 2)

    def test_order_by_same_type(self):
        qs = Number.objects.all()
        union = qs.union(qs)
        numbers = list(range(10))
        self.assertNumbersEqual(union.order_by('num'), numbers)
        self.assertNumbersEqual(union.order_by('other_num'), reversed(numbers))

    def test_unsupported_operations_on_combined_qs(self):
        qs = Number.objects.all()
        msg = 'Calling QuerySet.%s() after %s() is not supported.'
        combinators = ['union']
        if connection.features.supports_select_difference:
            combinators.append('difference')
        if connection.features.supports_select_intersection:
            combinators.append('intersection')
        for combinator in combinators:
            for operation in (
                'alias',
                'annotate',
                'defer',
                'delete',
                'distinct',
                'exclude',
                'extra',
                'filter',
                'only',
                'prefetch_related',
                'select_related',
                'update',
            ):
                with self.subTest(combinator=combinator, operation=operation):
                    with self.assertRaisesMessage(
                        NotSupportedError,
                        msg % (operation, combinator),
                    ):
                        getattr(getattr(qs, combinator)(qs), operation)()

    def test_get_with_filters_unsupported_on_combined_qs(self):
        qs = Number.objects.all()
        msg = 'Calling QuerySet.get(...) with filters after %s() is not supported.'
        combinators = ['union']
        if connection.features.supports_select_difference:
            combinators.append('difference')
        if connection.features.supports_select_intersection:
            combinators.append('intersection')
        for combinator in combinators:
            with self.subTest(combinator=combinator):
                with self.assertRaisesMessage(NotSupportedError, msg % combinator):
                    getattr(qs, combinator)(qs).get(num=2)
qs).get(num=2)
