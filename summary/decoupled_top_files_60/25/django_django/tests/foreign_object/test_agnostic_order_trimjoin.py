from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls):
        A class method that sets up test data for the entire test class.
        
        Parameters:
        cls (cls): The test class object.
        
        Returns:
        None
        
        Key Data Points:
        - Creates an instance of the Address model with company=1 and customer_id=20.
        - Creates an instance of the Customer model with company=1 and customer_id=20.
        - Creates an instance of the Contact model with company_code=1 and customer_code=20.
        
        This
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
        - self: The current test case instance.
        
        Input:
        - A Contact object linked to a Customer, which in turn is linked to an Address model.
        - An Address instance used for filtering.
        
        Output:
        - A boolean value indicating whether the query result matches the expected Contact object.
        
        Key Points:
        - The query filters Contacts based on the customer
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
