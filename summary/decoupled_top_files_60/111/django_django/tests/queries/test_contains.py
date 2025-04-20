from django.test import TestCase

from .models import DumbCategory, NamedCategory, ProxyCategory


class ContainsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = DumbCategory.objects.create()
        cls.proxy_category = ProxyCategory.objects.create()

    def test_unsaved_obj(self):
        """
        Test the behavior of the `contains` method on unsaved objects.
        
        This function checks if attempting to use the `contains` method on a Django QuerySet with an unsaved object raises a ValueError with the expected error message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the `contains` method does not raise a ValueError with the expected message when called on an unsaved object.
        
        Example:
        >>> test_unsaved_obj()
        ValueError: QuerySet.contains() cannot
        """

        msg = "QuerySet.contains() cannot be used on unsaved objects."
        with self.assertRaisesMessage(ValueError, msg):
            DumbCategory.objects.contains(DumbCategory())

    def test_obj_type(self):
        msg = "'obj' must be a model instance."
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.contains(object())

    def test_values(self):
        """
        Tests the behavior of the `contains` method on a QuerySet after applying `.values()` or `.values_list()` methods.
        
        This function checks that calling `contains` on a QuerySet that has already been transformed by `.values()` or `.values_list()` raises a TypeError with a specific message.
        
        Parameters:
        self: The instance of the test case class.
        
        Raises:
        TypeError: If `contains` is called on a QuerySet that has been transformed by `.values()` or `.values_list()`
        """

        msg = "Cannot call QuerySet.contains() after .values() or .values_list()."
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.values_list("pk").contains(self.category)
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.values("pk").contains(self.category)

    def test_basic(self):
        with self.assertNumQueries(1):
            self.assertIs(DumbCategory.objects.contains(self.category), True)
        # QuerySet.contains() doesn't evaluate a queryset.
        with self.assertNumQueries(1):
            self.assertIs(DumbCategory.objects.contains(self.category), True)

    def test_evaluated_queryset(self):
        qs = DumbCategory.objects.all()
        proxy_qs = ProxyCategory.objects.all()
        # Evaluate querysets.
        list(qs)
        list(proxy_qs)
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(self.category), True)
            self.assertIs(qs.contains(self.proxy_category), True)
            self.assertIs(proxy_qs.contains(self.category), True)
            self.assertIs(proxy_qs.contains(self.proxy_category), True)

    def test_proxy_model(self):
        """
        Tests the functionality of a proxy model.
        
        This function checks if a proxy model and its original model contain each other. It performs two database queries to verify the relationship between the proxy and the original model.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - `DumbCategory.objects.contains(self.proxy_category)` should return `True`.
        - `ProxyCategory.objects.contains(self.category)` should return `True`.
        
        Note:
        Each assertion is expected to execute a single database query.
        """

        with self.assertNumQueries(1):
            self.assertIs(DumbCategory.objects.contains(self.proxy_category), True)
        with self.assertNumQueries(1):
            self.assertIs(ProxyCategory.objects.contains(self.category), True)

    def test_wrong_model(self):
        qs = DumbCategory.objects.all()
        named_category = NamedCategory(name="category")
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
        # Evaluate the queryset.
        list(qs)
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
