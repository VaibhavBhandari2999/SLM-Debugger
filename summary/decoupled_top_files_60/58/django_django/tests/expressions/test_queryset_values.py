from django.db.models import F, Sum
from django.test import TestCase

from .models import Company, Employee


class ValuesExpressionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Company.objects.create(
            name='Example Inc.', num_employees=2300, num_chairs=5,
            ceo=Employee.objects.create(firstname='Joe', lastname='Smith', salary=10)
        )
        Company.objects.create(
            name='Foobar Ltd.', num_employees=3, num_chairs=4,
            ceo=Employee.objects.create(firstname='Frank', lastname='Meyer', salary=20)
        )
        Company.objects.create(
            name='Test GmbH', num_employees=32, num_chairs=1,
            ceo=Employee.objects.create(firstname='Max', lastname='Mustermann', salary=30)
        )

    def test_values_expression(self):
        """
        Tests the values expression of the Company model.
        
        This function asserts that the salary values of the Company objects are correctly retrieved using F expressions. The expected result is a list of dictionaries, each containing a 'salary' key with the corresponding salary value.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The values of the 'salary' field, obtained using F('ceo__salary'), should match the expected list of dictionaries: [{'salary': 10}, {'salary': 2
        """

        self.assertSequenceEqual(
            Company.objects.values(salary=F('ceo__salary')),
            [{'salary': 10}, {'salary': 20}, {'salary': 30}],
        )

    def test_values_expression_group_by(self):
        """
        Tests the behavior of the `values()` method in combination with `annotate()`.
        
        This function checks how `values()` and `annotate()` work together. Specifically, it tests how `values()` groups the results based on the specified fields and how `annotate()` is applied to these groups.
        
        Parameters:
        - None (the test data is created within the function)
        
        Returns:
        - None (the function asserts the expected results through `assertSequenceEqual`)
        
        Key Points:
        - `values()` applies `annotate()`
        """

        # values() applies annotate() first, so values selected are grouped by
        # id, not firstname.
        Employee.objects.create(firstname='Joe', lastname='Jones', salary=2)
        joes = Employee.objects.filter(firstname='Joe')
        self.assertSequenceEqual(
            joes.values('firstname', sum_salary=Sum('salary')).order_by('sum_salary'),
            [{'firstname': 'Joe', 'sum_salary': 2}, {'firstname': 'Joe', 'sum_salary': 10}],
        )
        self.assertSequenceEqual(
            joes.values('firstname').annotate(sum_salary=Sum('salary')),
            [{'firstname': 'Joe', 'sum_salary': 12}]
        )

    def test_chained_values_with_expression(self):
        Employee.objects.create(firstname='Joe', lastname='Jones', salary=2)
        joes = Employee.objects.filter(firstname='Joe').values('firstname')
        self.assertSequenceEqual(
            joes.values('firstname', sum_salary=Sum('salary')),
            [{'firstname': 'Joe', 'sum_salary': 12}]
        )
        self.assertSequenceEqual(
            joes.values(sum_salary=Sum('salary')),
            [{'sum_salary': 12}]
        )

    def test_values_list_expression(self):
        companies = Company.objects.values_list('name', F('ceo__salary'))
        self.assertSequenceEqual(companies, [('Example Inc.', 10), ('Foobar Ltd.', 20), ('Test GmbH', 30)])

    def test_values_list_expression_flat(self):
        companies = Company.objects.values_list(F('ceo__salary'), flat=True)
        self.assertSequenceEqual(companies, (10, 20, 30))
l(companies, (10, 20, 30))
