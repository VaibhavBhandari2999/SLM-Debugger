from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        A class method that sets up test data for the entire test class. This method is called once before any test method is run.
        
        Parameters:
        cls: The test class itself, used to create and store test data.
        
        Returns:
        None: This method does not return any value. It creates and stores test data for use in the test methods of the class.
        
        Key Actions:
        - Creates an Address object with company and customer_id fields.
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
        Tests the backward relationship query for a Contact model filtering by a customer's address.
        
        This function asserts that the query returns the correct Contact object based on the provided address.
        
        Parameters:
        - self (TestCase): The test case instance.
        
        Returns:
        - None: The function asserts the expected result and does not return any value.
        
        Key Parameters:
        - customer__address (QuerySet): The address used to filter the customer and subsequently the Contact objects.
        - contact1 (Contact): The expected Contact object that should be
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
