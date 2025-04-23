from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        A class method that sets up test data for the class. This method is used to create and initialize test data that will be reused across multiple test methods.
        
        Parameters:
        cls: The class object for which the test data is being set up.
        
        Returns:
        None: This method does not return any value. It creates and initializes test data objects (Address, Customer, and Contact) that are used in test methods.
        """

        cls.address = Address.objects.create(company=1, customer_id=20)
        cls.customer1 = Customer.objects.create(company=1, customer_id=20)
        cls.contact1 = Contact.objects.create(company_code=1, customer_code=20)

    def test_deep_mixed_forward(self):
        """
        Tests the deep mixed query filtering functionality.
        
        This function asserts that the query set returned by filtering `Address` objects based on the `customer__contacts` relationship with a specific `Contact` object matches the expected `Address` object.
        
        Parameters:
        self (TestInstance): The test instance, typically used in Django test cases.
        
        Returns:
        None: This function does not return any value. It raises an AssertionError if the query set does not match the expected result.
        
        Key Parameters:
        - `self
        """

        self.assertQuerysetEqual(
            Address.objects.filter(customer__contacts=self.contact1),
            [self.address.id],
            attrgetter('id')
        )

    def test_deep_mixed_backward(self):
        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
