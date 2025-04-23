from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        Summary:
        Sets up test data for the class. This method is used to create and initialize test data that will be shared among all test methods in the class.
        
        Parameters:
        cls: The class object. This parameter is used to access class attributes and methods.
        
        Returns:
        None: This method does not return any value. It is used to set up the test environment.
        
        Key Data Points:
        - `address`: An instance
        """

        cls.address = Address.objects.create(company=1, customer_id=20)
        cls.customer1 = Customer.objects.create(company=1, customer_id=20)
        cls.contact1 = Contact.objects.create(company_code=1, customer_code=20)

    def test_deep_mixed_forward(self):
        """
        Tests the deep mixed query filtering functionality.
        
        This function asserts that the Address objects associated with the customer, which in turn is linked to the specified contact (self.contact1), match the expected queryset. The expected result is a queryset containing the ID of a single address (self.address.id).
        
        Parameters:
        - None
        
        Keywords:
        - self: The test case instance, necessary for accessing self.contact1 and self.address.
        
        Returns:
        - None
        
        Raises:
        - AssertionError: If the filtered queryset does not match the
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
