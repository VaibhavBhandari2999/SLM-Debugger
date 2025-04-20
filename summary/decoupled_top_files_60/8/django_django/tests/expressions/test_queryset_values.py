from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from django.test import TestCase

from .models import Company, Employee


class ValuesExpressionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Company and Employee models.
        
        This method creates three instances of the Company model and populates them with related Employee instances. Each Company instance is associated with a unique Employee who serves as the CEO.
        
        Key Parameters:
        - None (this is a class method that operates on the class level)
        
        Returns:
        - None (populates the database with test data)
        
        Example Usage:
        ```python
        class MyTest(TestCase):
        @classmethod
        def setUpTestData(cls):
        super().setUp
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
        Tests the values expression for the salary field, which is derived from the ceo's salary. The function asserts that the returned list of dictionaries contains the correct salary values for each company.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses the `values` method to retrieve the salary field.
        - The salary field is calculated using F-expression to reference the ceo's salary.
        - The expected output is a list of dictionaries, each containing a single key
        """

        self.assertSequenceEqual(
            Company.objects.values(salary=F('ceo__salary')),
            [{'salary': 10}, {'salary': 20}, {'salary': 30}],
        )

    def test_values_expression_group_by(self):
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
        Tests the functionality of chaining values and expressions in Django ORM.
        
        This function creates an employee record and then performs two tests:
        1. It filters employees with the first name 'Joe', retrieves their first names, and calculates the sum of their salaries.
        2. It performs the same filtering and salary sum calculation but without explicitly specifying the first name.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - Uses Django ORM's `Employee.objects.create` to create a record.
        - Uses `values
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
