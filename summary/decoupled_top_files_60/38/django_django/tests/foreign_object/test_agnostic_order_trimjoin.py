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
        cls: The class object. This is used to access class attributes and methods.
        
        Returns:
        None: This method does not return any value. It is used to set up the test environment by creating instances of Address, Customer, and Contact models.
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
        Tests the deep mixed backward relationship query.
        
        This function asserts that the queryset returned by filtering `Contact` objects based on a `customer__address` relationship contains the expected contact ID.
        
        Parameters:
        - self (TestInstance): The test instance context.
        
        Input:
        - `Contact.objects.filter(customer__address=self.address)`: A filtered queryset of `Contact` objects where the `customer` has the specified `address`.
        
        Output:
        - A list of contact IDs that match the filter criteria, expected to be `[
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
