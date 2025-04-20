from django.db.models import F, Sum
from django.test import TestCase

from .models import Company, Employee


class ValuesExpressionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Company and Employee models.
        
        This method creates three instances of the Company model with associated Employee instances. Each Company instance is linked to a corresponding Employee instance representing the CEO of the company.
        
        Key Parameters:
        - None (This method uses class-level attributes and does not take any parameters)
        
        Keywords:
        - Company: A model representing a company with attributes such as name, number of employees, and number of chairs.
        - Employee: A model representing an employee with attributes such as first name
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
        Tests the functionality of chaining values with expressions in Django ORM.
        
        This function creates an employee record and then filters employees with the firstname 'Joe'.
        It then checks if the chained values with expressions are working correctly. Specifically, it verifies:
        1. The 'firstname' field is correctly retrieved.
        2. The 'sum_salary' field, which is the sum of 'salary' for all filtered employees, is correctly calculated and returned.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The
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
