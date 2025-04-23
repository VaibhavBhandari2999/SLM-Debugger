from operator import attrgetter

from django.test.testcases import TestCase

from .models import Address, Contact, Customer


class TestLookupQuery(TestCase):
    @classmethod
    def setUpTestData(cls):
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
        """
        Tests the backward relationship query on a deeply nested model.
        
        This function asserts that the query set returned by filtering `Contact` objects
        based on a nested `customer__address` relationship matches the expected contact
        ID. The query is expected to return a single `Contact` object with the ID
        self.contact1.id.
        
        Parameters:
        - self: The test case instance, used to access test data such as `self.address` and `self.contact1`.
        
        Returns:
        - None: This function asserts the
        """

        self.assertQuerySetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter("id"),
        )
