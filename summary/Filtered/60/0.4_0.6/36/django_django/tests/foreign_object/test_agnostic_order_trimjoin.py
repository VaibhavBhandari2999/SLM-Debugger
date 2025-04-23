from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        A class method that sets up test data for the class. This method is used to create and initialize test data that will be shared across multiple test methods within the same class.
        
        Parameters:
        cls: The class object for which the test data is being set up. This is a reference to the class itself, allowing the method to modify class-level attributes.
        
        Returns:
        None: This method does not return any value. It is used to create and store
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
        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
