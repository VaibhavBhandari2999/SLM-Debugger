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
        """
        Tests the behavior of the `contains` method when provided with an object that is not a model instance.
        
        Parameters:
        None
        
        Raises:
        TypeError: If the input 'obj' is not a model instance, with the message "'obj' must be a model instance."
        
        Example:
        >>> DumbCategory.objects.contains(object())
        Raises a TypeError with the message "'obj' must be a model instance."
        """

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
        with self.assertNumQueries(1):
            self.assertIs(DumbCategory.objects.contains(self.proxy_category), True)
        with self.assertNumQueries(1):
            self.assertIs(ProxyCategory.objects.contains(self.category), True)

    def test_wrong_model(self):
        """
        Tests the behavior of the `contains` method with a model that does not support it.
        
        This function checks if a queryset of `DumbCategory` objects contains a `NamedCategory` instance. The `DumbCategory` model is expected to not support the `contains` method, so the `contains` check should always return `False`. The function ensures that no database queries are executed during the `contains` check and that the queryset is evaluated only once.
        
        Parameters:
        None
        
        Returns:
        """

        qs = DumbCategory.objects.all()
        named_category = NamedCategory(name="category")
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
        # Evaluate the queryset.
        list(qs)
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
  self.assertIs(qs.contains(named_category), False)
