from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        A class method that sets up test data for the class. This method is intended to be used in Django test cases to create test data that can be reused across multiple test methods.
        
        Parameters:
        - cls: The test class instance. This parameter is used to access class attributes and methods.
        
        Key Data Points:
        - `Address`: An instance of the Address model is created with `company=1` and `customer_id=20`.
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
        Tests the backward relationship in a deep query involving a mixed model setup.
        
        This function filters contacts based on their associated customer's address and checks if the resulting queryset matches the expected contact.
        
        Parameters:
        - self (TestInstance): The test instance that contains the necessary setup and assertions.
        
        Input:
        - self.address (Address): The address object used for filtering.
        - self.contact1 (Contact): The expected contact object that should be in the resulting queryset.
        
        Output:
        - A boolean value indicating whether the test passed
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
