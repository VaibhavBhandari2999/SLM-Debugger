from django.core.exceptions import ValidationError
from django.test import TestCase, skipUnlessDBFeature

from .models import (
    ChildProduct,
    ChildUniqueConstraintProduct,
    Product,
    UniqueConstraintConditionProduct,
    UniqueConstraintProduct,
)


class PerformConstraintChecksTest(TestCase):
    @skipUnlessDBFeature("supports_table_check_constraints")
    def test_full_clean_with_check_constraints(self):
        product = Product(price=10, discounted_price=15)
        with self.assertRaises(ValidationError) as cm:
            product.full_clean()
        self.assertEqual(
            cm.exception.message_dict,
            {
                "__all__": [
                    "Constraint “price_gt_discounted_price_validation” is violated."
                ]
            },
        )

    @skipUnlessDBFeature("supports_table_check_constraints")
    def test_full_clean_with_check_constraints_on_child_model(self):
        product = ChildProduct(price=10, discounted_price=15)
        with self.assertRaises(ValidationError) as cm:
            product.full_clean()
        self.assertEqual(
            cm.exception.message_dict,
            {
                "__all__": [
                    "Constraint “price_gt_discounted_price_validation” is violated."
                ]
            },
        )

    @skipUnlessDBFeature("supports_table_check_constraints")
    def test_full_clean_with_check_constraints_disabled(self):
        product = Product(price=10, discounted_price=15)
        product.full_clean(validate_constraints=False)

    def test_full_clean_with_unique_constraints(self):
        """
        Tests the full_clean method for models with unique constraints.
        
        This function checks the full_clean method for models that have unique constraints. It creates an instance of a `UniqueConstraintProduct` with a specific name, color, and rank, and then attempts to create another instance with the same values. This is done to test the behavior of the full_clean method when unique constraints are violated.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValidationError: If the unique constraints are not properly enforced during
        """

        UniqueConstraintProduct.objects.create(name="product", color="yellow", rank=1)
        tests = [
            UniqueConstraintProduct(name="product", color="yellow", rank=1),
            # Child model.
            ChildUniqueConstraintProduct(name="product", color="yellow", rank=1),
        ]
        for product in tests:
            with self.subTest(model=product.__class__.__name__):
                with self.assertRaises(ValidationError) as cm:
                    product.full_clean()
                self.assertEqual(
                    cm.exception.message_dict,
                    {
                        "__all__": [
                            "Unique constraint product with this Name and Color "
                            "already exists."
                        ],
                        "rank": [
                            "Unique constraint product with this Rank already exists."
                        ],
                    },
                )

    def test_full_clean_with_unique_constraints_disabled(self):
        """
        Tests the `full_clean` method of a model instance with unique constraints disabled.
        
        This method creates a `UniqueConstraintProduct` instance with specific attributes and calls the `full_clean` method with `validate_constraints=False`. This is useful for testing scenarios where unique constraints should be bypassed.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - `name`: The name of the product.
        - `color`: The color of the product.
        - `rank`: The rank of
        """

        UniqueConstraintProduct.objects.create(name="product", color="yellow", rank=1)
        product = UniqueConstraintProduct(name="product", color="yellow", rank=1)
        product.full_clean(validate_constraints=False)

    @skipUnlessDBFeature("supports_partial_indexes")
    def test_full_clean_with_partial_unique_constraints(self):
        UniqueConstraintConditionProduct.objects.create(name="product")
        product = UniqueConstraintConditionProduct(name="product")
        with self.assertRaises(ValidationError) as cm:
            product.full_clean()
        self.assertEqual(
            cm.exception.message_dict,
            {
                "__all__": [
                    "Constraint “name_without_color_uniq_validation” is violated."
                ]
            },
        )

    @skipUnlessDBFeature("supports_partial_indexes")
    def test_full_clean_with_partial_unique_constraints_disabled(self):
        """
        Tests the `full_clean` method with partial unique constraints disabled for a `UniqueConstraintConditionProduct` model.
        
        Parameters:
        None
        
        Key Parameters:
        - `UniqueConstraintConditionProduct`: The model instance being tested.
        
        Keywords:
        - `validate_constraints`: A boolean flag to disable validation of unique constraints during the clean process. Set to `False` in this test.
        
        Output:
        - None. The function asserts that the `full_clean` method does not raise a `ValidationError` when unique
        """

        UniqueConstraintConditionProduct.objects.create(name="product")
        product = UniqueConstraintConditionProduct(name="product")
        product.full_clean(validate_constraints=False)
