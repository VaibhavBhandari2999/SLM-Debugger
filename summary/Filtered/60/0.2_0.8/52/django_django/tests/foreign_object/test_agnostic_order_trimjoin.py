from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        A class method that sets up test data for the class. This method is used to create and initialize test data that will be shared across all test methods within the class.
        
        Parameters:
        - cls: The test class itself, used to access class attributes and methods.
        
        Returns:
        - None: This method does not return any value. It is used to set up the test environment.
        
        Usage:
        This method is typically used in Django
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
        
        This function asserts that the queryset returned by filtering `Contact` objects based on a `customer__address` relationship matches the expected `Contact` object. The expected `Contact` object is identified by its ID.
        
        Parameters:
        - self (unittest.TestCase): The test case instance.
        
        Keywords:
        - address (Address): The `Address` object used for filtering.
        - contact1 (Contact): The `Contact` object expected to be in the queryset.
        
        Returns:
        -
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
