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
        """
        Tests the deep mixed query filtering functionality.
        
        This function asserts that the query set returned by filtering `Address` objects based on the `customer__contacts` relationship with a specific `Contact` object matches the expected `Address` object.
        
        Parameters:
        - self: The test case instance.
        
        Keywords:
        - contact1: The specific `Contact` object used for filtering.
        
        Returns:
        - None: This function asserts the equality of the query set and the expected result, raising an AssertionError if they do not match.
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
