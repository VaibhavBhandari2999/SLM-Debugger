from django.db.models import BooleanField, Exists, F, OuterRef, Q
from django.db.models.expressions import RawSQL
from django.test import SimpleTestCase

from .models import Tag


class QTests(SimpleTestCase):
    def test_combine_and_empty(self):
        """
        Test the combination of Q objects with an empty Q object.
        
        Parameters:
        q (Q): A Q object with a condition.
        
        Returns:
        None: This function asserts the equality of combined Q objects and does not return any value.
        
        This function checks that combining a Q object with an empty Q object using the bitwise AND operator (&) results in the original Q object. It performs this check for two scenarios:
        1. A Q object with a simple condition (e.g., x=1).
        2
        """

        q = Q(x=1)
        self.assertEqual(q & Q(), q)
        self.assertEqual(Q() & q, q)

        q = Q(x__in={}.keys())
        self.assertEqual(q & Q(), q)
        self.assertEqual(Q() & q, q)

    def test_combine_and_both_empty(self):
        self.assertEqual(Q() & Q(), Q())

    def test_combine_or_empty(self):
        """
        Test the behavior of combining a query with an empty query.
        
        This function tests the logical OR operation between a non-empty query and an empty query. It ensures that combining a non-empty query with an empty query results in the non-empty query itself, regardless of the order of combination.
        
        Parameters:
        q (Q): A non-empty query object.
        
        Returns:
        None: This function asserts the expected behavior and does not return any value.
        
        Examples:
        >>> q = Q(x=1)
        >>>
        """

        q = Q(x=1)
        self.assertEqual(q | Q(), q)
        self.assertEqual(Q() | q, q)

        q = Q(x__in={}.keys())
        self.assertEqual(q | Q(), q)
        self.assertEqual(Q() | q, q)

    def test_combine_empty_copy(self):
        base_q = Q(x=1)
        tests = [
            base_q | Q(),
            Q() | base_q,
            base_q & Q(),
            Q() & base_q,
        ]
        for i, q in enumerate(tests):
            with self.subTest(i=i):
                self.assertEqual(q, base_q)
                self.assertIsNot(q, base_q)

    def test_combine_or_both_empty(self):
        self.assertEqual(Q() | Q(), Q())

    def test_combine_not_q_object(self):
        obj = object()
        q = Q(x=1)
        with self.assertRaisesMessage(TypeError, str(obj)):
            q | obj
        with self.assertRaisesMessage(TypeError, str(obj)):
            q & obj

    def test_combine_negated_boolean_expression(self):
        """
        Tests the negation of boolean expressions involving the existence of related objects.
        
        This function tests two specific boolean expressions that involve the negation of the existence of related objects. The expressions are evaluated for their negated status.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        The function uses the `Tag` model and the `OuterRef` object to filter tags by category. It then constructs two boolean expressions using the `Q` object and the `Exists` lookup. The expressions are:
        1. `
        """

        tagged = Tag.objects.filter(category=OuterRef('pk'))
        tests = [
            Q() & ~Exists(tagged),
            Q() | ~Exists(tagged),
        ]
        for q in tests:
            with self.subTest(q=q):
                self.assertIs(q.negated, True)

    def test_deconstruct(self):
        q = Q(price__gt=F('discounted_price'))
        path, args, kwargs = q.deconstruct()
        self.assertEqual(path, 'django.db.models.Q')
        self.assertEqual(args, (('price__gt', F('discounted_price')),))
        self.assertEqual(kwargs, {})

    def test_deconstruct_negated(self):
        q = ~Q(price__gt=F('discounted_price'))
        path, args, kwargs = q.deconstruct()
        self.assertEqual(args, (('price__gt', F('discounted_price')),))
        self.assertEqual(kwargs, {'_negated': True})

    def test_deconstruct_or(self):
        """
        Tests the deconstruction of a logical OR query involving two Q objects.
        
        This function tests the deconstruction of a Django QuerySet's Q object that uses the logical OR operator. The Q objects are created with specific conditions and combined using the OR operator. The deconstructed representation of the combined Q object is then compared to expected values.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Parameters:
        - q1: A Q object with the condition 'price__gt=F('discounted_price')'.
        """

        q1 = Q(price__gt=F('discounted_price'))
        q2 = Q(price=F('discounted_price'))
        q = q1 | q2
        path, args, kwargs = q.deconstruct()
        self.assertEqual(args, (
            ('price__gt', F('discounted_price')),
            ('price', F('discounted_price')),
        ))
        self.assertEqual(kwargs, {'_connector': 'OR'})

    def test_deconstruct_and(self):
        q1 = Q(price__gt=F('discounted_price'))
        q2 = Q(price=F('discounted_price'))
        q = q1 & q2
        path, args, kwargs = q.deconstruct()
        self.assertEqual(args, (
            ('price__gt', F('discounted_price')),
            ('price', F('discounted_price')),
        ))
        self.assertEqual(kwargs, {})

    def test_deconstruct_multiple_kwargs(self):
        q = Q(price__gt=F('discounted_price'), price=F('discounted_price'))
        path, args, kwargs = q.deconstruct()
        self.assertEqual(args, (
            ('price', F('discounted_price')),
            ('price__gt', F('discounted_price')),
        ))
        self.assertEqual(kwargs, {})

    def test_deconstruct_nested(self):
        q = Q(Q(price__gt=F('discounted_price')))
        path, args, kwargs = q.deconstruct()
        self.assertEqual(args, (Q(price__gt=F('discounted_price')),))
        self.assertEqual(kwargs, {})

    def test_deconstruct_boolean_expression(self):
        """
        Tests the deconstruction of a boolean expression.
        
        This function tests the deconstruction of a boolean expression represented by a RawSQL object. The expression '1 = 1' is used as an example, which is a common boolean expression that always evaluates to True. The expression is wrapped in a Q object, which is a utility for constructing complex query expressions. The deconstruct method is then called on the Q object to break it down into its constituent parts.
        
        Parameters:
        - expr (RawSQL): A
        """

        expr = RawSQL('1 = 1', BooleanField())
        q = Q(expr)
        _, args, kwargs = q.deconstruct()
        self.assertEqual(args, (expr,))
        self.assertEqual(kwargs, {})

    def test_reconstruct(self):
        """
        Tests the deconstruction of a Q object with a conditional filter.
        
        This function checks if the deconstructed Q object can be reconstructed
        correctly. The Q object is initialized with a conditional filter that
        compares the 'price' field to the 'discounted_price' field using the 'gt'
        operator (greater than). The function deconstructs the Q object and then
        compares the deconstructed Q object with the original one to ensure they
        are equivalent.
        
        Parameters:
        None
        
        Returns
        """

        q = Q(price__gt=F('discounted_price'))
        path, args, kwargs = q.deconstruct()
        self.assertEqual(Q(*args, **kwargs), q)

    def test_reconstruct_negated(self):
        q = ~Q(price__gt=F('discounted_price'))
        path, args, kwargs = q.deconstruct()
        self.assertEqual(Q(*args, **kwargs), q)

    def test_reconstruct_or(self):
        q1 = Q(price__gt=F('discounted_price'))
        q2 = Q(price=F('discounted_price'))
        q = q1 | q2
        path, args, kwargs = q.deconstruct()
        self.assertEqual(Q(*args, **kwargs), q)

    def test_reconstruct_and(self):
        q1 = Q(price__gt=F('discounted_price'))
        q2 = Q(price=F('discounted_price'))
        q = q1 & q2
        path, args, kwargs = q.deconstruct()
        self.assertEqual(Q(*args, **kwargs), q)
