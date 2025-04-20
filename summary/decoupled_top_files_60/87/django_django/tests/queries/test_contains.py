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
        
        This function checks if the `contains` method of the `DumbCategory` model's
        queryset raises a `ValueError` with the expected error message when an unsaved
        object is passed to it.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the error message does not match the expected message.
        """

        msg = 'QuerySet.contains() cannot be used on unsaved objects.'
        with self.assertRaisesMessage(ValueError, msg):
            DumbCategory.objects.contains(DumbCategory())

    def test_obj_type(self):
        msg = "'obj' must be a model instance."
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.contains(object())

    def test_values(self):
        """
        Tests the behavior of the `contains` method on a QuerySet after applying `.values()` or `.values_list()` methods.
        
        Key Parameters:
        - `self`: The test case instance.
        
        Key Methods:
        - `values_list('pk')`: Returns a QuerySet with only the primary key values.
        - `values('pk')`: Returns a QuerySet with only the primary key field as a dictionary.
        
        Key Assertions:
        - Raises a `TypeError` with the message: 'Cannot call QuerySet.contains()
        """

        msg = 'Cannot call QuerySet.contains() after .values() or .values_list().'
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.values_list('pk').contains(self.category)
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.values('pk').contains(self.category)

    def test_basic(self):
        """
        Tests the basic functionality of the `contains` method on a QuerySet.
        
        This method checks if a given category is contained within a queryset. The test ensures that the `contains` method does not evaluate the queryset and that the same query is used for multiple checks.
        
        Parameters:
        - self: The test case instance.
        
        Assertions:
        - The first `assertIs` checks if the category is contained in the queryset, expecting `True`.
        - The second `assertIs` does the same check, expecting `
        """

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
        qs = DumbCategory.objects.all()
        named_category = NamedCategory(name='category')
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
        # Evaluate the queryset.
        list(qs)
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
