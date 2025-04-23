from django.test import TestCase

from .models import DumbCategory, NamedCategory, ProxyCategory


class ContainsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = DumbCategory.objects.create()
        cls.proxy_category = ProxyCategory.objects.create()

    def test_unsaved_obj(self):
        msg = "QuerySet.contains() cannot be used on unsaved objects."
        with self.assertRaisesMessage(ValueError, msg):
            DumbCategory.objects.contains(DumbCategory())

    def test_obj_type(self):
        msg = "'obj' must be a model instance."
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.contains(object())

    def test_values(self):
        """
        Tests the behavior of the `contains` method on a QuerySet after applying `.values()` or `.values_list()`.
        
        This function checks that calling `contains` on a QuerySet that has already been modified by `.values()` or `.values_list()` raises a TypeError with a specific message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If `contains` is called on a QuerySet that has been modified by `.values()` or `.values_list()`.
        
        Key Points:
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
        """
        Tests the behavior of evaluated QuerySets for both DumbCategory and ProxyCategory models.
        
        This function evaluates the QuerySets for both DumbCategory and ProxyCategory models and then checks if the contains method returns the expected results for both a regular category and a proxy category.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Evaluates the QuerySets for DumbCategory and ProxyCategory models.
        - Uses the contains method to check if the QuerySets contain specific category instances.
        - Verifies
        """

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
        with self.assertNumQueries(1):
            self.assertIs(DumbCategory.objects.contains(self.proxy_category), True)
        with self.assertNumQueries(1):
            self.assertIs(ProxyCategory.objects.contains(self.category), True)

    def test_wrong_model(self):
        """
        Tests the behavior of the `contains` method with a model that does not support it.
        
        This function checks if a queryset of `DumbCategory` objects contains a `NamedCategory` instance. The `DumbCategory` model does not support the `contains` method, so the `contains` check should always return `False`. The function ensures that no database queries are executed during the `contains` check and that the result remains `False` even after evaluating the queryset.
        
        Parameters:
        None
        """

        qs = DumbCategory.objects.all()
        named_category = NamedCategory(name="category")
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
        # Evaluate the queryset.
        list(qs)
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
