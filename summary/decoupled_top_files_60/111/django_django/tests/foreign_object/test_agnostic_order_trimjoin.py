from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        This method is a class method used to set up test data for a test class. It is typically used in Django tests to create objects that are shared across multiple test methods.
        
        Parameters:
        - cls: The test class itself, passed as the first argument.
        
        Returns:
        - None: This method does not return any value. It creates and saves objects to the database.
        
        Key Actions:
        - Creates an Address object with company=1 and customer_id=20.
        - Creates a
        """

        cls.address = Address.objects.create(company=1, customer_id=20)
        cls.customer1 = Customer.objects.create(company=1, customer_id=20)
        cls.contact1 = Contact.objects.create(company_code=1, customer_code=20)

    def test_deep_mixed_forward(self):
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
