from datetime import datetime

from django.core.exceptions import FieldError
from django.db.models import CharField, F, Q
from django.db.models.expressions import SimpleCol
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
        query = Query(Author)
        where = query.build_where(Q(num__gt=2))
        lookup = where.children[0]
        self.assertIsInstance(lookup, GreaterThan)
        self.assertEqual(lookup.rhs, 2)
        self.assertEqual(lookup.lhs.target, Author._meta.get_field('num'))

    def test_simplecol_query(self):
        """
        Tests the construction of a simple column query.
        
        This function checks the construction of a query using the `Query` class for the `Author` model. It builds a query with a complex `WHERE` clause involving a combination of `GreaterThan`, `IsNull`, and `LessThan` lookups. The function verifies that the constructed query has the expected structure and that the correct types of lookups are used.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The `GreaterThan` lookup for
        """

        query = Query(Author)
        where = query.build_where(Q(num__gt=2, name__isnull=False) | Q(num__lt=F('id')))

        name_isnull_lookup, num_gt_lookup = where.children[0].children
        self.assertIsInstance(num_gt_lookup, GreaterThan)
        self.assertIsInstance(num_gt_lookup.lhs, SimpleCol)
        self.assertIsInstance(name_isnull_lookup, IsNull)
        self.assertIsInstance(name_isnull_lookup.lhs, SimpleCol)

        num_lt_lookup = where.children[1]
        self.assertIsInstance(num_lt_lookup, LessThan)
        self.assertIsInstance(num_lt_lookup.rhs, SimpleCol)
        self.assertIsInstance(num_lt_lookup.lhs, SimpleCol)

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
        query = Query(Item)
        where = query.build_where(Q(modified__gt=F('created')))
        lookup = where.children[0]
        self.assertIsInstance(lookup, GreaterThan)
        self.assertIsInstance(lookup.rhs, SimpleCol)
        self.assertIsInstance(lookup.lhs, SimpleCol)
        self.assertEqual(lookup.rhs.target, Item._meta.get_field('created'))
        self.assertEqual(lookup.lhs.target, Item._meta.get_field('modified'))

    def test_transform(self):
        """
        Tests the transformation of a query with a custom lookup.
        
        This function checks if the transformation of a query with a custom `Lower` lookup works as expected. It registers the `Lower` lookup for the `CharField`, builds a query with a negated `Q` object, and then inspects the resulting `Where` node to ensure that it contains an `Exact` lookup with the correct `Lower` and `SimpleCol` components.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key
        """

        query = Query(Author)
        with register_lookup(CharField, Lower):
            where = query.build_where(~Q(name__lower='foo'))
        lookup = where.children[0]
        self.assertIsInstance(lookup, Exact)
        self.assertIsInstance(lookup.lhs, Lower)
        self.assertIsInstance(lookup.lhs.lhs, SimpleCol)
        self.assertEqual(lookup.lhs.lhs.target, Author._meta.get_field('name'))

    def test_negated_nullable(self):
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
        query = Query(Item)
        msg = 'Joined field references are not permitted in this query'
        with self.assertRaisesMessage(FieldError, msg):
            query.build_where(Q(creator__num__gt=2))

    def test_foreign_key_f(self):
        """
        Tests the behavior of a query involving a foreign key relationship.
        
        This function checks if a query involving a foreign key relationship raises a FieldError as expected. It builds a query using the `Ranking` model and attempts to use the `F` expression to reference a field from the related model (`author__num`). If the query is built successfully without raising an exception, it indicates a potential issue with the handling of foreign key relationships in the query construction.
        
        Parameters:
        None
        
        Returns:
        None
        """

        query = Query(Ranking)
        with self.assertRaises(FieldError):
            query.build_where(Q(rank__gt=F('author__num')))

    def test_foreign_key_exclusive(self):
        """
        Tests the creation of a WHERE clause for a Query object involving foreign key exclusivity.
        
        This function constructs a WHERE clause for a Query object that checks if either 'objecta' or 'objectb' is None in an ObjectC model. It then verifies that the constructed WHERE clause consists of two RelatedIsNull nodes, each checking if a foreign key is null. The function asserts that the left-hand side (lhs) of each RelatedIsNull node is a SimpleCol and that it correctly references the 'object
        """

        query = Query(ObjectC)
        where = query.build_where(Q(objecta=None) | Q(objectb=None))
        a_isnull = where.children[0]
        self.assertIsInstance(a_isnull, RelatedIsNull)
        self.assertIsInstance(a_isnull.lhs, SimpleCol)
        self.assertEqual(a_isnull.lhs.target, ObjectC._meta.get_field('objecta'))
        b_isnull = where.children[1]
        self.assertIsInstance(b_isnull, RelatedIsNull)
        self.assertIsInstance(b_isnull.lhs, SimpleCol)
        self.assertEqual(b_isnull.lhs.target, ObjectC._meta.get_field('objectb'))

    def test_clone_select_related(self):
        """
        Function: test_clone_select_related
        
        This function tests the behavior of the `clone` method in the `Query` class, specifically focusing on the `add_select_related` method.
        
        Parameters:
        - self: The test case object provided by the testing framework.
        
        Returns:
        - None: This function is a test case and does not return any value. It asserts the correctness of the `clone` and `add_select_related` methods.
        
        Description:
        - The function creates an instance of `Query` for
        """

        query = Query(Item)
        query.add_select_related(['creator'])
        clone = query.clone()
        clone.add_select_related(['note', 'creator__extra'])
        self.assertEqual(query.select_related, {'creator': {}})
