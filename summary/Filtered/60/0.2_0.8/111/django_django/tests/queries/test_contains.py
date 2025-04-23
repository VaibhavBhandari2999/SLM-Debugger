from django.test import TestCase

from .models import DumbCategory, NamedCategory, ProxyCategory


class ContainsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = DumbCategory.objects.create()
        cls.proxy_category = ProxyCategory.objects.create()

    def test_unsaved_obj(self):
        """
        Tests the behavior of the `contains` method on unsaved objects.
        
        This function asserts that attempting to use the `contains` method on a Django QuerySet with an unsaved object raises a ValueError with a specific message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the `contains` method is called on a QuerySet with an unsaved object, a ValueError is raised with the message "QuerySet.contains() cannot be used on unsaved objects."
        
        Example Usage:
        """

        msg = "QuerySet.contains() cannot be used on unsaved objects."
        with self.assertRaisesMessage(ValueError, msg):
            DumbCategory.objects.contains(DumbCategory())

    def test_obj_type(self):
        msg = "'obj' must be a model instance."
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.contains(object())

    def test_values(self):
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
        Tests the behavior of proxy models in relation to category containment.
        
        This function checks if a proxy model and its original model correctly identify containment of categories.
        
        Parameters:
        self (unittest.TestCase): The test case instance.
        
        Assertions:
        - Verifies that the `DumbCategory` proxy model correctly identifies the `self.proxy_category` as contained.
        - Verifies that the `ProxyCategory` model correctly identifies the `self.category` as contained.
        
        Each assertion is checked with a single database query.
        """

        with self.assertNumQueries(1):
            self.assertIs(DumbCategory.objects.contains(self.proxy_category), True)
        with self.assertNumQueries(1):
            self.assertIs(ProxyCategory.objects.contains(self.category), True)

    def test_wrong_model(self):
        """
        Tests the behavior of the `contains` method with a wrong model instance.
        
        This function checks if a queryset of `DumbCategory` objects contains an instance of `NamedCategory`. The `contains` method should return `False` for a wrong model instance. The test ensures that the `contains` method does not execute any database queries when checking for a wrong model instance and that the result remains consistent even after evaluating the queryset.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        -
        """

        qs = DumbCategory.objects.all()
        named_category = NamedCategory(name="category")
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
        # Evaluate the queryset.
        list(qs)
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
