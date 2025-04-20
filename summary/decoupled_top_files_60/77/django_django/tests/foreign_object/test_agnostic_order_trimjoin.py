from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        A class method that sets up test data for the class. This method is called once before any tests are run for the class.
        
        Parameters:
        cls (class): The class in which this method is defined. The test data is created for this class.
        
        Returns:
        None: This method does not return anything. It creates and sets up test data for the class.
        
        Key Data Points:
        - Creates an instance of the Address model with company=1
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
        
        This function verifies that filtering a Contact queryset by a related customer's address correctly returns the expected Contact object.
        
        Parameters:
        - self: The current test case instance.
        
        Returns:
        - None: This function asserts the equality of the expected and actual query results, raising an AssertionError if they do not match.
        
        Key Elements:
        - `Contact.objects.filter(customer__address=self.address)`: Filters the Contact queryset by the customer's address.
        - `[self
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
