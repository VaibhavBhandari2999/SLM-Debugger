from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        This method is a class method used to set up test data for a test class. It is intended to be called before any test method runs.
        
        Parameters:
        cls (class): The test class in which this method is defined.
        
        Returns:
        None: This method does not return any value. It creates and initializes test data objects for use in test methods.
        
        Key Data Points:
        - `address`: An instance of the `Address` model, linked to a company and
        """

        cls.address = Address.objects.create(company=1, customer_id=20)
        cls.customer1 = Customer.objects.create(company=1, customer_id=20)
        cls.contact1 = Contact.objects.create(company_code=1, customer_code=20)

    def test_deep_mixed_forward(self):
        """
        Tests the deep mixed query filtering for the Address model.
        This function filters the Address objects where the customer has a contact that matches the provided contact1.
        The expected result is a queryset containing the address with the specified ID.
        
        Parameters:
        - self: The current test case instance.
        
        Returns:
        - None: This function asserts the equality of the filtered queryset with the expected result and does not return any value.
        
        Key Parameters:
        - contact1: The contact object used to filter the customer and subsequently the
        """

        self.assertQuerySetEqual(
            Address.objects.filter(customer__contacts=self.contact1),
            [self.address.id],
            attrgetter("id"),
        )

    def test_deep_mixed_backward(self):
        self.assertQuerySetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter("id"),
        )
