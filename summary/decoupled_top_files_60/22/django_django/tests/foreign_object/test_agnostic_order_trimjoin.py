from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        This method is a class method used to set up test data for a test class. It is called once before any tests are run for the class.
        
        Parameters:
        cls: The test class itself, passed as the first argument.
        
        Returns:
        None. This method populates the test class with predefined test data.
        
        Key Data Points:
        - `address`: An instance of the `Address` model, linked to a company with `company=1` and a customer with `
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
        Tests the backward relationship in a deep query involving mixed model types.
        
        This function asserts that the query filters contacts based on their associated customer's address and returns the correct contact IDs.
        
        Parameters:
        - self (TestCase): The test case instance.
        
        Returns:
        - None: The function asserts the expected result and does not return any value.
        
        Key Elements:
        - `Contact.objects.filter(customer__address=self.address)`: Filters contacts where the customer's address matches the provided address.
        - `[self.contact1.id]`:
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
