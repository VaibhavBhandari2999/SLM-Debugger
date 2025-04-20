from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls):
        A class method that sets up test data for the class. This method is intended to be used in Django test cases to create test data that can be shared across multiple test methods.
        
        Parameters:
        cls: The test class instance. This parameter is used to access class attributes and methods.
        
        Returns:
        None: This method does not return any value. It creates and populates database objects for testing purposes.
        
        Key Data Points:
        - cls.address: An instance of the Address
        """

        cls.address = Address.objects.create(company=1, customer_id=20)
        cls.customer1 = Customer.objects.create(company=1, customer_id=20)
        cls.contact1 = Contact.objects.create(company_code=1, customer_code=20)

    def test_deep_mixed_forward(self):
        self.assertQuerysetEqual(
            Address.objects.filter(customer__contacts=self.contact1),
            [self.address.id],
            attrgetter('id')
        )

    def test_deep_mixed_backward(self):
        """
        Tests the backward relationship filtering in a deep query.
        
        This function asserts that the query returns the correct Contact objects based on the provided customer's address.
        
        Parameters:
        - self: The current test case instance.
        
        Input:
        - self.address: The address object of the customer.
        - self.contact1: The contact object to be filtered.
        
        Output:
        - The function uses assertQuerysetEqual to check if the query returns the expected Contact object IDs.
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
