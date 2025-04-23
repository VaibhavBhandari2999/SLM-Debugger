from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls):
        A class method that sets up test data for the class. It creates instances of the Address, Customer, and Contact models and assigns them to class variables.
        
        Parameters:
        cls: The class object for which the test data is being set up.
        
        Returns:
        None: This method does not return any value. It populates class variables with test data for use in test methods.
        
        Key Details:
        - Creates an Address instance and assigns it to cls.address.
        - Creates a
        """

        cls.address = Address.objects.create(company=1, customer_id=20)
        cls.customer1 = Customer.objects.create(company=1, customer_id=20)
        cls.contact1 = Contact.objects.create(company_code=1, customer_code=20)

    def test_deep_mixed_forward(self):
        """
        Tests the deep mixed query filtering functionality.
        
        This function verifies that the `Address` objects associated with a specific `customer` and their related `contacts` can be correctly filtered. The query filters `Address` instances where the `customer` has a `contact` that matches `self.contact1`.
        
        Parameters:
        - self: The test case instance (required for test methods in Django tests).
        
        Returns:
        - None: This function asserts the equality of the query result with the expected output, hence it does not
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
