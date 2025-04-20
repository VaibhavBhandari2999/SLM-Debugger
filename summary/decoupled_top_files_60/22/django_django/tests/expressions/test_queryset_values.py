from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from django.test import TestCase

from .models import Company, Employee


class ValuesExpressionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Company and Employee models.
        
        This method creates three instances of the Company model with associated Employee instances as CEOs. Each Company instance is populated with specific attributes such as name, number of employees, number of chairs, and the CEO's details.
        
        Key Parameters:
        - None (This method is a class method and is called on the class itself)
        
        Returns:
        - None (This method populates the database with test data and does not return any value)
        
        Example Usage:
        ```python
        """

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
        self.assertSequenceEqual(
            Company.objects.values(salary=F('ceo__salary')),
            [{'salary': 10}, {'salary': 20}, {'salary': 30}],
        )

    def test_values_expression_group_by(self):
        """
        Tests the behavior of the `values()` method in combination with `annotate()`.
        
        This function checks how `values()` interacts with `annotate()` when used to group by different fields. Specifically, it tests the following:
        - `values()` applies `annotate()` first, so the values selected are grouped by the primary key (id) rather than the specified field (firstname).
        - The `sum_salary` field is calculated using `Sum('salary')`.
        
        The function creates an `Employee` object and filters
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
        """
        Tests the chaining of values with expressions in Django ORM.
        
        This function creates an employee record and then performs a query to filter employees with the first name 'Joe'.
        It then tests the chaining of the `values` method with aggregation expressions to sum the salaries of the filtered employees.
        The function asserts that the results match the expected output.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Methods:
        - `Employee.objects.create(firstname='Joe', lastname='Jones', salary=2)`: Creates an
        """

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
