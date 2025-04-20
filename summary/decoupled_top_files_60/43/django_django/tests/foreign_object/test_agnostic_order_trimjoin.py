from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        A class method that sets up test data for the class. This method is used to create and initialize test data that will be shared across all test methods in the class.
        
        Parameters:
        - cls: The class object for which the test data is being set up.
        
        Returns:
        - None: This method does not return any value. It creates and initializes test data objects (Address, Customer, Contact) that are used in test methods.
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
        
        This function asserts that the query returns the correct Contact object based on the specified filter criteria.
        
        Parameters:
        - self (TestInstance): The test instance, used for asserting the queryset equality.
        
        Returns:
        - None: This function does not return any value. It raises an AssertionError if the query does not match the expected result.
        
        Key Parameters:
        - self.address (Address): The address object used for filtering the customer.
        - contact1 (Contact
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
