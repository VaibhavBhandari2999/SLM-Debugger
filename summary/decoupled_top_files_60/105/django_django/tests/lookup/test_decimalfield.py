from django.db.models import F, Sum
from django.test import TestCase

from .models import Product, Stock


class DecimalFieldLookupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Product and Stock models.
        
        This method creates instances of the Product and Stock models for testing purposes. It populates the database with four Product objects, each associated with multiple Stock objects. The Product objects are annotated with the sum of available quantities from their associated Stock objects and the difference between the target quantity and the sum of available quantities.
        
        Key Parameters:
        - None (This is a class method and is called on the class itself)
        
        Returns:
        - None (Modifies the class
        """

        cls.p1 = Product.objects.create(name="Product1", qty_target=10)
        Stock.objects.create(product=cls.p1, qty_available=5)
        Stock.objects.create(product=cls.p1, qty_available=6)
        cls.p2 = Product.objects.create(name="Product2", qty_target=10)
        Stock.objects.create(product=cls.p2, qty_available=5)
        Stock.objects.create(product=cls.p2, qty_available=5)
        cls.p3 = Product.objects.create(name="Product3", qty_target=10)
        Stock.objects.create(product=cls.p3, qty_available=5)
        Stock.objects.create(product=cls.p3, qty_available=4)
        cls.queryset = Product.objects.annotate(
            qty_available_sum=Sum("stock__qty_available"),
        ).annotate(qty_needed=F("qty_target") - F("qty_available_sum"))

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
