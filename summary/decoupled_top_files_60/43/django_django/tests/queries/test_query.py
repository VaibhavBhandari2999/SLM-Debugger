from datetime import datetime

from django.core.exceptions import FieldError
from django.db.models import BooleanField, CharField, F, Q
from django.db.models.expressions import Col, Func
from django.db.models.fields.related_lookups import RelatedIsNull
from django.db.models.functions import Lower
from django.db.models.lookups import Exact, GreaterThan, IsNull, LessThan
from django.db.models.sql.query import Query
from django.db.models.sql.where import OR
from django.test import SimpleTestCase
from django.test.utils import register_lookup

from .models import Author, Item, ObjectC, Ranking


class TestQuery(SimpleTestCase):
    def test_simple_query(self):
        """
        Tests the construction of a simple query with a greater than condition.
        
        This function tests the `build_where` method of the `Query` class for a simple query involving a greater than condition. It creates a query for the `Author` model and builds a where clause with the condition that the `num` field should be greater than 2. The function then checks if the generated where clause contains a `GreaterThan` lookup with the correct right-hand side value and the correct field reference.
        
        Parameters:
        """

        query = Query(Author)
        where = query.build_where(Q(num__gt=2))
        lookup = where.children[0]
        self.assertIsInstance(lookup, GreaterThan)
        self.assertEqual(lookup.rhs, 2)
        self.assertEqual(lookup.lhs.target, Author._meta.get_field('num'))

    def test_non_alias_cols_query(self):
        query = Query(Author, alias_cols=False)
        where = query.build_where(Q(num__gt=2, name__isnull=False) | Q(num__lt=F('id')))

        name_isnull_lookup, num_gt_lookup = where.children[0].children
        self.assertIsInstance(num_gt_lookup, GreaterThan)
        self.assertIsInstance(num_gt_lookup.lhs, Col)
        self.assertIsNone(num_gt_lookup.lhs.alias)
        self.assertIsInstance(name_isnull_lookup, IsNull)
        self.assertIsInstance(name_isnull_lookup.lhs, Col)
        self.assertIsNone(name_isnull_lookup.lhs.alias)

        num_lt_lookup = where.children[1]
        self.assertIsInstance(num_lt_lookup, LessThan)
        self.assertIsInstance(num_lt_lookup.rhs, Col)
        self.assertIsNone(num_lt_lookup.rhs.alias)
        self.assertIsInstance(num_lt_lookup.lhs, Col)
        self.assertIsNone(num_lt_lookup.lhs.alias)

    def test_complex_query(self):
        query = Query(Author)
        where = query.build_where(Q(num__gt=2) | Q(num__lt=0))
        self.assertEqual(where.connector, OR)

        lookup = where.children[0]
        self.assertIsInstance(lookup, GreaterThan)
        self.assertEqual(lookup.rhs, 2)
        self.assertEqual(lookup.lhs.target, Author._meta.get_field('num'))

        lookup = where.children[1]
        self.assertIsInstance(lookup, LessThan)
        self.assertEqual(lookup.rhs, 0)
        self.assertEqual(lookup.lhs.target, Author._meta.get_field('num'))

    def test_multiple_fields(self):
        query = Query(Item, alias_cols=False)
        where = query.build_where(Q(modified__gt=F('created')))
        lookup = where.children[0]
        self.assertIsInstance(lookup, GreaterThan)
        self.assertIsInstance(lookup.rhs, Col)
        self.assertIsNone(lookup.rhs.alias)
        self.assertIsInstance(lookup.lhs, Col)
        self.assertIsNone(lookup.lhs.alias)
        self.assertEqual(lookup.rhs.target, Item._meta.get_field('created'))
        self.assertEqual(lookup.lhs.target, Item._meta.get_field('modified'))

    def test_transform(self):
        query = Query(Author, alias_cols=False)
        with register_lookup(CharField, Lower):
            where = query.build_where(~Q(name__lower='foo'))
        lookup = where.children[0]
        self.assertIsInstance(lookup, Exact)
        self.assertIsInstance(lookup.lhs, Lower)
        self.assertIsInstance(lookup.lhs.lhs, Col)
        self.assertIsNone(lookup.lhs.lhs.alias)
        self.assertEqual(lookup.lhs.lhs.target, Author._meta.get_field('name'))

    def test_negated_nullable(self):
        """
        Tests the negation of a nullable query condition.
        
        This function tests the construction of a query where a nullable field is checked for values not less than a specified date. The query is built using the `~Q` negation operator. The resulting query is expected to have a negated condition and should include a `LessThan` lookup for the 'modified' field and an `IsNull` lookup for the same field, indicating that the field can be null and not less than the specified date.
        
        Parameters
        """

        query = Query(Item)
        where = query.build_where(~Q(modified__lt=datetime(2017, 1, 1)))
        self.assertTrue(where.negated)
        lookup = where.children[0]
        self.assertIsInstance(lookup, LessThan)
        self.assertEqual(lookup.lhs.target, Item._meta.get_field('modified'))
        lookup = where.children[1]
        self.assertIsInstance(lookup, IsNull)
        self.assertEqual(lookup.lhs.target, Item._meta.get_field('modified'))

    def test_foreign_key(self):
        """
        Tests the behavior of a query involving a foreign key reference.
        
        This function checks if a query involving a foreign key reference is handled correctly. It attempts to build a query using the `Q` object to filter items based on a related field (`creator__num`). If the query is successfully built, it indicates that foreign key references are permitted. If the query fails, a `FieldError` is expected, with a specific error message indicating that joined field references are not permitted.
        
        Parameters:
        None
        """

        query = Query(Item)
        msg = 'Joined field references are not permitted in this query'
        with self.assertRaisesMessage(FieldError, msg):
            query.build_where(Q(creator__num__gt=2))

    def test_foreign_key_f(self):
        query = Query(Ranking)
        with self.assertRaises(FieldError):
            query.build_where(Q(rank__gt=F('author__num')))

    def test_foreign_key_exclusive(self):
        query = Query(ObjectC, alias_cols=False)
        where = query.build_where(Q(objecta=None) | Q(objectb=None))
        a_isnull = where.children[0]
        self.assertIsInstance(a_isnull, RelatedIsNull)
        self.assertIsInstance(a_isnull.lhs, Col)
        self.assertIsNone(a_isnull.lhs.alias)
        self.assertEqual(a_isnull.lhs.target, ObjectC._meta.get_field('objecta'))
        b_isnull = where.children[1]
        self.assertIsInstance(b_isnull, RelatedIsNull)
        self.assertIsInstance(b_isnull.lhs, Col)
        self.assertIsNone(b_isnull.lhs.alias)
        self.assertEqual(b_isnull.lhs.target, ObjectC._meta.get_field('objectb'))

    def test_clone_select_related(self):
        """
        Function: test_clone_select_related
        
        This function tests the behavior of the `clone` method of a Query object, specifically focusing on the `add_select_related` method.
        
        Parameters:
        - self: The current test case instance.
        
        Returns:
        - None: This function is a test case and does not return any value. It asserts the correctness of the `clone` and `add_select_related` methods.
        
        Description:
        - The function creates a Query object for the Item model and adds a select related clause
        """

        query = Query(Item)
        query.add_select_related(['creator'])
        clone = query.clone()
        clone.add_select_related(['note', 'creator__extra'])
        self.assertEqual(query.select_related, {'creator': {}})

    def test_iterable_lookup_value(self):
        query = Query(Item)
        where = query.build_where(Q(name=['a', 'b']))
        name_exact = where.children[0]
        self.assertIsInstance(name_exact, Exact)
        self.assertEqual(name_exact.rhs, "['a', 'b']")

    def test_filter_conditional(self):
        query = Query(Item)
        where = query.build_where(Func(output_field=BooleanField()))
        exact = where.children[0]
        self.assertIsInstance(exact, Exact)
        self.assertIsInstance(exact.lhs, Func)
        self.assertIs(exact.rhs, True)

    def test_filter_conditional_join(self):
        query = Query(Item)
        filter_expr = Func('note__note', output_field=BooleanField())
        msg = 'Joined field references are not permitted in this query'
        with self.assertRaisesMessage(FieldError, msg):
            query.build_where(filter_expr)

    def test_filter_non_conditional(self):
        """
        Tests the behavior of filtering with a non-conditional expression.
        
        This function tests whether a `TypeError` is raised when attempting to filter
        against a non-conditional expression using the `Func` object. The `Func` object
        is used to create a non-conditional expression, which should not be used for
        filtering.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If the `Func` object is used for filtering, a `TypeError` is
        expected
        """

        query = Query(Item)
        msg = 'Cannot filter against a non-conditional expression.'
        with self.assertRaisesMessage(TypeError, msg):
            query.build_where(Func(output_field=CharField()))
re(Func(output_field=CharField()))
