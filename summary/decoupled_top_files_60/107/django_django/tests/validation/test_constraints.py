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
        
        This function creates an instance of the Product model with a price of 10 and a discounted_price of 15. It then attempts to validate the instance using the full_clean method. The function expects a ValidationError to be raised due to a check constraint violation. The error message should indicate that the "price_gt_discounted_price_validation" constraint is violated.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError:
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
        """
        Test the full_clean method with check constraints on a child model.
        
        This test ensures that the full_clean method raises a ValidationError when a check constraint on the child model is violated.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the check constraint "price_gt_discounted_price_validation" is violated.
        
        Example:
        >>> product = ChildProduct(price=10, discounted_price=15)
        >>> with self.assertRaises(ValidationError) as cm:
        ...     product.full
        """

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
        Tests the full_clean method for a model with partial unique constraints disabled.
        
        This method creates an instance of UniqueConstraintConditionProduct with a name "product" and attempts to validate it without checking constraints. It is used to verify that the model instance can be saved even if some unique constraints are not fully enforced.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A UniqueConstraintConditionProduct instance with name "product" is created.
        - The full_clean method is called with validate
        """

        UniqueConstraintConditionProduct.objects.create(name="product")
        product = UniqueConstraintConditionProduct(name="product")
        product.full_clean(validate_constraints=False)
aints=False)
