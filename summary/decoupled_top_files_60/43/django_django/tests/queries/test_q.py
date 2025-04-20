from django.db.models import F, Q
from django.test import SimpleTestCase


class QTests(SimpleTestCase):
    def test_combine_and_empty(self):
        """
        Test combining QuerySet objects with an empty query.
        
        Parameters:
        q (Q): A QuerySet object with a condition 'x=1'.
        
        Returns:
        None: This function asserts conditions rather than returning a value.
        
        Description:
        This test function checks the behavior of combining a non-empty QuerySet object with an empty one using the '&' operator. It asserts that the result of the combination is the non-empty QuerySet object itself, demonstrating that an empty QuerySet does not alter the non-empty one
        """

        q = Q(x=1)
        self.assertEqual(q & Q(), q)
        self.assertEqual(Q() & q, q)

    def test_combine_and_both_empty(self):
        self.assertEqual(Q() & Q(), Q())

    def test_combine_or_empty(self):
        q = Q(x=1)
        self.assertEqual(q | Q(), q)
        self.assertEqual(Q() | q, q)

    def test_combine_or_both_empty(self):
        self.assertEqual(Q() | Q(), Q())

    def test_combine_not_q_object(self):
        obj = object()
        q = Q(x=1)
        with self.assertRaisesMessage(TypeError, str(obj)):
            q | obj
        with self.assertRaisesMessage(TypeError, str(obj)):
            q & obj

    def test_deconstruct(self):
        q = Q(price__gt=F('discounted_price'))
        path, args, kwargs = q.deconstruct()
        self.assertEqual(path, 'django.db.models.Q')
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {'price__gt': F('discounted_price')})

    def test_deconstruct_negated(self):
        """
        Tests the deconstruction of a negated query.
        
        This function checks the deconstruction of a negated query object. The query being tested is `~Q(price__gt=F('discounted_price'))`, which negates the condition that the price is greater than the discounted price. The deconstruction process breaks down the query into its component parts for easier manipulation or serialization.
        
        Parameters:
        None
        
        Returns:
        None
        
        The function asserts that:
        - The `args` parameter of the deconstructed query
        """

        q = ~Q(price__gt=F('discounted_price'))
        path, args, kwargs = q.deconstruct()
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {
            'price__gt': F('discounted_price'),
            '_negated': True,
        })

    def test_deconstruct_or(self):
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
        """
        Tests the deconstruction of a Q object with multiple kwargs.
        
        This function verifies that the deconstruction of a Q object with multiple kwargs works as expected. The Q object is initialized with two kwargs: 'price__gt=F('discounted_price')' and 'price=F('discounted_price')'. The function then deconstructs the Q object and checks that the resulting arguments and keyword arguments match the expected values.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The args tuple should
        """

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

    def test_reconstruct(self):
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
        """
        Tests the reconstruction of a query object that combines two conditions using the AND operator.
        
        Args:
        q1 (Q): A query object representing the first condition (price greater than discounted price).
        q2 (Q): A query object representing the second condition (price equal to discounted price).
        
        Returns:
        None: The function asserts that the reconstructed query object is equivalent to the original combined query object.
        """

        q1 = Q(price__gt=F('discounted_price'))
        q2 = Q(price=F('discounted_price'))
        q = q1 & q2
        path, args, kwargs = q.deconstruct()
        self.assertEqual(Q(*args, **kwargs), q)
