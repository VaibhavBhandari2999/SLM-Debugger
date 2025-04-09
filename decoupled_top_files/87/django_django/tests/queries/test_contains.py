"""
The provided Python file is a Django test case (`ContainsTests`) designed to validate the behavior of the `contains` method on Django QuerySets. The `contains` method is crucial for determining whether a given model instance is contained within a queryset. The test cases cover various scenarios including:

- **Unsaved Objects**: Ensuring that the `contains` method raises a `ValueError` when applied to unsaved objects.
- **Input Type Validation**: Confirming that the method requires a model instance as input and raises a `TypeError` otherwise.
- **QuerySet Transformation**: Verifying that the `contains` method cannot be used on QuerySets that have been transformed by methods like `.values()` or `.values_list()`.
- **Basic Functionality
"""
from django.test import TestCase

from .models import DumbCategory, NamedCategory, ProxyCategory


class ContainsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = DumbCategory.objects.create()
        cls.proxy_category = ProxyCategory.objects.create()

    def test_unsaved_obj(self):
        """
        Test that QuerySet.contains() raises a ValueError when used on an unsaved object.
        
        This function checks if using `DumbCategory.objects.contains()` on an unsaved instance of `DumbCategory` raises a `ValueError` with the expected error message.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the error message does not match the expected message.
        
        Important Functions:
        - `DumbCategory.objects.contains()`: The method being tested
        """

        msg = 'QuerySet.contains() cannot be used on unsaved objects.'
        with self.assertRaisesMessage(ValueError, msg):
            DumbCategory.objects.contains(DumbCategory())

    def test_obj_type(self):
        """
        Test that the 'contains' method requires a model instance as input.
        
        - Input: A non-model instance object.
        - Output: Raises a TypeError with the message: "'obj' must be a model instance."
        
        Important Functions:
        - `self.assertRaisesMessage`: Used to assert that a specific exception is raised with a given message.
        - `DumbCategory.objects.contains`: The method being tested, which should raise an error if a non-model instance is passed.
        """

        msg = "'obj' must be a model instance."
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.contains(object())

    def test_values(self):
        """
        Raises a TypeError if a QuerySet containing values is used with the contains method.
        
        This function tests whether calling `contains` on a QuerySet that has
        already been transformed by `.values()` or `.values_list()` will raise
        a TypeError with an appropriate message.
        
        Args:
        self: The instance of the class containing this method.
        
        Raises:
        TypeError: If the `contains` method is called on a QuerySet that has
        already been transformed by `.values()`
        """

        msg = 'Cannot call QuerySet.contains() after .values() or .values_list().'
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.values_list('pk').contains(self.category)
        with self.assertRaisesMessage(TypeError, msg):
            DumbCategory.objects.values('pk').contains(self.category)

    def test_basic(self):
        """
        Tests the basic functionality of the `contains` method on a queryset. Ensures that the method does not evaluate the queryset and returns the same result in a single query.
        
        Args:
        self: The test case instance.
        
        Assertions:
        - Verifies that the `contains` method returns `True` for the given category.
        - Ensures that only one database query is executed during the evaluation.
        """

        with self.assertNumQueries(1):
            self.assertIs(DumbCategory.objects.contains(self.category), True)
        # QuerySet.contains() doesn't evaluate a queryset.
        with self.assertNumQueries(1):
            self.assertIs(DumbCategory.objects.contains(self.category), True)

    def test_evaluated_queryset(self):
        """
        Tests the evaluation of querysets and their containment checks.
        
        This function evaluates two different querysets, `qs` and `proxy_qs`, by converting them to lists. It then performs containment checks using the `contains` method on both the original and proxy querysets, ensuring that the results are as expected.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `list()`: Evaluates the querysets by converting them to lists.
        - `ProxyCategory
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
        """
        Tests the behavior of proxy models in relation to the `contains` method.
        
        This function verifies that both the original and proxy models correctly identify
        whether one category contains another using the `contains` method. It asserts that
        the `DumbCategory` model returns `True` when checking if it contains the `proxy_category`,
        and similarly, the `ProxyCategory` model returns `True` when checking if it contains
        the `category`.
        
        The function uses `assertNum
        """

        with self.assertNumQueries(1):
            self.assertIs(DumbCategory.objects.contains(self.proxy_category), True)
        with self.assertNumQueries(1):
            self.assertIs(ProxyCategory.objects.contains(self.category), True)

    def test_wrong_model(self):
        """
        Tests the behavior of the `contains` method with a wrong model instance.
        
        This function checks whether a queryset of `DumbCategory` objects contains
        an instance of `NamedCategory`. The `contains` method is expected to return
        `False` for a wrong model instance. The function uses `assertNumQueries` to
        ensure that no additional database queries are executed during the checks.
        """

        qs = DumbCategory.objects.all()
        named_category = NamedCategory(name='category')
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
        # Evaluate the queryset.
        list(qs)
        with self.assertNumQueries(0):
            self.assertIs(qs.contains(named_category), False)
