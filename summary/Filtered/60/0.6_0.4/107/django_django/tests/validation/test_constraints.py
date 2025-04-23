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
        Tests the full_clean method with check constraints.
        
        This function checks if the full_clean method raises a ValidationError when the check constraint "price_gt_discounted_price_validation" is violated. The Product model is used with a price of 10 and a discounted_price of 15. The expected error message is that the constraint "price_gt_discounted_price_validation" is violated.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the check constraint is not violated as expected.
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
        UniqueConstraintConditionProduct.objects.create(name="product")
        product = UniqueConstraintConditionProduct(name="product")
        product.full_clean(validate_constraints=False)
t.full_clean(validate_constraints=False)
