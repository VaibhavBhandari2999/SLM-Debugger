from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the class.
        
        This method creates instances of `Address`, `Customer`, and `Contact` models with predefined attributes. The `setUpTestData` method is a class-level setup function that initializes test data for all tests within the class.
        
        Args:
        cls: The class object on which the method is called.
        
        Returns:
        None
        
        Important Functions:
        - `Address.objects.create()`: Creates an instance of the `Address` model.
        - `Customer
        """

        cls.address = Address.objects.create(company=1, customer_id=20)
        cls.customer1 = Customer.objects.create(company=1, customer_id=20)
        cls.contact1 = Contact.objects.create(company_code=1, customer_code=20)

    def test_deep_mixed_forward(self):
        """
        Tests the deep mixed query filtering functionality.
        
        This function asserts that the queryset returned by filtering `Address` objects based on their associated `customer` and `customer__contacts` relationships, with a specific `Contact` instance (`self.contact1`), matches the expected result, which is a queryset containing the ID of a single `Address` object (`self.address.id`).
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `assertQuerysetEqual`: Comp
        """

        self.assertQuerysetEqual(
            Address.objects.filter(customer__contacts=self.contact1),
            [self.address.id],
            attrgetter('id')
        )

    def test_deep_mixed_backward(self):
        """
        Tests the backward relationship query on a deep, mixed queryset.
        
        This function filters `Contact` objects based on their associated `customer`
        having a specific `address`. It asserts that the resulting queryset contains
        only the ID of the expected `contact1`.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `filter`: Used to filter `Contact` objects.
        - `assertQuerysetEqual`: Asserts the equality of the filtered queryset.
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
