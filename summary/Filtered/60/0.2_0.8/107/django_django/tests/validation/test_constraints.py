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
        """
        Tests the full_clean method of a Product model with check constraints.
        
        This function creates a Product instance with a price of 10 and a discounted_price of 15. It then attempts to validate the instance using the full_clean method. The method is expected to raise a ValidationError due to a check constraint that ensures the price is greater than the discounted_price. The error message should indicate that the "price_gt_discounted_price_validation" constraint is violated.
        
        Parameters:
        None
        
        Returns:
        None
        """

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
        Tests the full_clean method with partial unique constraints disabled for a UniqueConstraintConditionProduct model.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the product fails validation due to unique constraints.
        
        Key Parameters:
        - `validate_constraints` (bool): A flag indicating whether to validate constraints during full_clean. Set to False to disable validation of unique constraints.
        
        Note:
        This test creates a product with a name 'product' and then attempts to create another product with the same
        """

        UniqueConstraintConditionProduct.objects.create(name="product")
        product = UniqueConstraintConditionProduct(name="product")
        product.full_clean(validate_constraints=False)
