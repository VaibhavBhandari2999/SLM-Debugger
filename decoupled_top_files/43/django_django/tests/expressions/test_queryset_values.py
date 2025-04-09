from django.db.models import F, Sum
from django.test import TestCase

from .models import Company, Employee


class ValuesExpressionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for company and employee objects.
        
        This method creates three `Company` instances with associated `Employee` objects. Each company is initialized with specific attributes such as name, number of employees, number of chairs, and a CEO. The CEO is created using the `Employee` model and assigned a salary.
        
        Input:
        - None
        
        Output:
        - Three `Company` objects with their respective attributes and one `Employee` object per company.
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
        """
        Tests the values expression of Company objects, ensuring that the salary is correctly fetched from the ceo__salary field. The function asserts that the returned values match the expected list of dictionaries containing salary values [10, 20, 30].
        """

        self.assertSequenceEqual(
            Company.objects.values(salary=F('ceo__salary')),
            [{'salary': 10}, {'salary': 20}, {'salary': 30}],
        )

    def test_values_expression_group_by(self):
        """
        Tests the behavior of the `values()` method when used with aggregation functions like `Sum`. The `values()` method groups the results based on the specified fields, but when combined with aggregation functions, it processes each group separately. This function creates employee records, filters them by first name, and then tests two scenarios:
        1. Using `values()` directly with an aggregation function (`Sum`), resulting in multiple grouped entries.
        2. Using `annotate()` with an aggregation function before
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
        Tests the behavior of chained values with expressions in Django ORM.
        
        This function creates an employee record, filters employees by first name,
        and then tests the output of `values` method with and without specified
        expressions. The `values` method is used to retrieve specific fields from
        the database query results, while `Sum` is used to calculate the total
        salary of the filtered employees.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        -
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
