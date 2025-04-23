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
        Test the deep mixed forward relationship query.
        
        This function asserts that the queryset returned by filtering `Address` objects based on a `customer` that has a `contact` matching `self.contact1` is equal to a queryset containing the `id` of `self.address`.
        
        Parameters:
        - self: The current test case instance.
        
        Keywords:
        - customer__contacts: A double-underscore lookup used to filter `Address` objects through the `customer` relationship to `Contact` objects.
        
        Input:
        -
        """

        self.assertQuerysetEqual(
            Address.objects.filter(customer__contacts=self.contact1),
            [self.address.id],
            attrgetter('id')
        )

    def test_deep_mixed_backward(self):
        """
        Tests the backward relationship in a deep query involving mixed types.
        
        This function asserts that the queryset returned by filtering `Contact` objects
        based on a `customer__address` relationship contains the expected contact ID.
        
        Parameters:
        - self (TestInstance): The test instance, typically a subclass of `TestCase`.
        
        Input:
        - `self.address`: An instance of the `Address` model used for filtering.
        - `self.contact1`: An instance of the `Contact` model expected to be in the result.
        """

        self.assertQuerysetEqual(
            Contact.objects.filter(customer__address=self.address),
            [self.contact1.id],
            attrgetter('id')
        )
