from django.db.models import F, Sum
from django.test import TestCase

from .models import Product, Stock


class DecimalFieldLookupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        Sets up test data for the Product and Stock models.
        
        Parameters:
        cls (class): The class in which the test data is being set up.
        
        Returns:
        None: This method does not return any value. It populates the database with test data.
        
        Key Data Points:
        - Creates three Product objects (p1, p2, p3) with a target quantity of 10 each.
        - For each Product, creates two Stock
        """

        cls.p1 = Product.objects.create(name='Product1', qty_target=10)
        Stock.objects.create(product=cls.p1, qty_available=5)
        Stock.objects.create(product=cls.p1, qty_available=6)
        cls.p2 = Product.objects.create(name='Product2', qty_target=10)
        Stock.objects.create(product=cls.p2, qty_available=5)
        Stock.objects.create(product=cls.p2, qty_available=5)
        cls.p3 = Product.objects.create(name='Product3', qty_target=10)
        Stock.objects.create(product=cls.p3, qty_available=5)
        Stock.objects.create(product=cls.p3, qty_available=4)
        cls.queryset = Product.objects.annotate(
            qty_available_sum=Sum('stock__qty_available'),
        ).annotate(qty_needed=F('qty_target') - F('qty_available_sum'))

    def test_gt(self):
        qs = self.queryset.filter(qty_needed__gt=0)
        self.assertCountEqual(qs, [self.p3])

    def test_gte(self):
        qs = self.queryset.filter(qty_needed__gte=0)
        self.assertCountEqual(qs, [self.p2, self.p3])

    def test_lt(self):
        qs = self.queryset.filter(qty_needed__lt=0)
        self.assertCountEqual(qs, [self.p1])

    def test_lte(self):
        qs = self.queryset.filter(qty_needed__lte=0)
        self.assertCountEqual(qs, [self.p1, self.p2])
