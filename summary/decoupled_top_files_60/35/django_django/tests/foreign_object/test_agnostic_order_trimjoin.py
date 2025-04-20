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
        cls: The test class instance.
        
        Returns:
        None. This method populates the test class with pre-defined objects for testing purposes.
        
        Key Objects Created:
        - cls.address: An instance of the Address model with company=1 and customer_id=20.
        - cls.customer1: An instance of the
        """

        cls.address = Address.objects.create(company=1, customer_id=20)
        cls.customer1 = Customer.objects.create(company=1, customer_id=20)
        cls.contact1 = Contact.objects.create(company_code=1, customer_code=20)

    def test_deep_mixed_forward(self):
        """
        Tests the deep mixed query filtering functionality.
        
        This function asserts that the query set returned by filtering `Address` objects based on a specific `customer` and `contacts` relationship matches the expected `Address` object. The query filters `Address` objects where the `customer` has a `contacts` relationship with a given `contact1` object.
        
        Parameters:
        self: The current test case instance.
        
        Keywords:
        - `customer__contacts=self.contact1`: Filters `Address` objects where the `
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
          attrgetter('id')
        )
