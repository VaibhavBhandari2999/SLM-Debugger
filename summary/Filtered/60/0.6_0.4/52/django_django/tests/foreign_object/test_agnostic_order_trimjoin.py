from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        ------------------------------------------------------------------------
        Sets up test data for the class.
        
        Parameters:
        cls (cls): The class object where the test data will be set up.
        
        Returns:
        None: This method does not return any value. It sets up the test data for the class.
        
        Description:
        This method is used to create and set up test data for the class. It creates an instance of the Address, Customer, and Contact models with predefined attributes and assigns them to class variables for use in
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
        
        This function asserts that the query returns the correct Contact object based on the provided address. It filters the Contact objects where the customer has the specified address and checks if the result matches the expected Contact ID.
        
        Parameters:
        - self.address (Address): The address object used for filtering.
        
        Returns:
        - None: The function asserts the expected result and does not return any value.
        
        Key Points:
        - The function uses `assertQuerysetEqual` to
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
