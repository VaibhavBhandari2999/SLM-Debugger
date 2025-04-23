from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls):
        This method is used to set up test data for a test class. It is called once before any test method is run.
        
        Parameters:
        cls (class): The test class object.
        
        Returns:
        None: This method does not return anything. It creates and initializes test data for the test class.
        
        Key Data Points:
        - `address`: An instance of the `Address` model with `company` set to 1 and `customer_id`
        """

        cls.address = Address.objects.create(company=1, customer_id=20)
        cls.customer1 = Customer.objects.create(company=1, customer_id=20)
        cls.contact1 = Contact.objects.create(company_code=1, customer_code=20)

    def test_deep_mixed_forward(self):
        self.assertQuerySetEqual(
            Address.objects.filter(customer__contacts=self.contact1),
            [self.address.id],
            attrgetter("id"),
        )

    def test_deep_mixed_backward(self):
        """
        Tests the backward relationship in a deep query involving a mixed model setup.
        
        This function asserts that the query set returned by filtering `Contact` objects based on a related `customer` which has a related `address` matches the expected result. Specifically, it filters `Contact` objects where the `customer` has the given `address` and checks if the resulting query set contains the expected `Contact` object.
        
        Parameters:
        - self: The current test case instance.
        - address: The `Address` object
        """

        self.assertQuerySetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter("id"),
        )
