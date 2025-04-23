from django.db.models import F, Sum
from django.test import TestCase

from .models import Company, Employee


class ValuesExpressionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Company and Employee models.
        
        This method creates three instances of the Company model with associated Employee instances as CEOs. Each Company instance is initialized with specific attributes such as name, number of employees, number of chairs, and the CEO's details (firstname, lastname, and salary).
        
        Key Parameters:
        - None (This method is a class method and is called on the class itself)
        
        Returns:
        - None (This method populates the database with test data and does not return any value
        """

        Company.objects.create(
            name="Example Inc.",
            num_employees=2300,
            num_chairs=5,
            ceo=Employee.objects.create(firstname="Joe", lastname="Smith", salary=10),
        )
        Company.objects.create(
            name="Foobar Ltd.",
            num_employees=3,
            num_chairs=4,
            ceo=Employee.objects.create(firstname="Frank", lastname="Meyer", salary=20),
        )
        Company.objects.create(
            name="Test GmbH",
            num_employees=32,
            num_chairs=1,
            ceo=Employee.objects.create(
                firstname="Max", lastname="Mustermann", salary=30
            ),
        )

    def test_values_expression(self):
        """
        Tests the values expression for the Company model.
        
        This function asserts that the values expression correctly retrieves the salary of each company's CEO. The expression uses F expression to reference the CEO's salary field.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Assertions:
        - The returned values should match the expected list of dictionaries, where each dictionary contains a 'salary' key with the corresponding CEO's salary.
        """

        self.assertSequenceEqual(
            Company.objects.values(salary=F("ceo__salary")),
            [{"salary": 10}, {"salary": 20}, {"salary": 30}],
        )

    def test_values_expression_alias_sql_injection(self):
        crafted_alias = """injected_name" from "expressions_company"; --"""
        msg = (
            "Column aliases cannot contain whitespace characters, quotation marks, "
            "semicolons, or SQL comments."
        )
        with self.assertRaisesMessage(ValueError, msg):
            Company.objects.values(**{crafted_alias: F("ceo__salary")})

    def test_values_expression_group_by(self):
        # values() applies annotate() first, so values selected are grouped by
        # id, not firstname.
        Employee.objects.create(firstname="Joe", lastname="Jones", salary=2)
        joes = Employee.objects.filter(firstname="Joe")
        self.assertSequenceEqual(
            joes.values("firstname", sum_salary=Sum("salary")).order_by("sum_salary"),
            [
                {"firstname": "Joe", "sum_salary": 2},
                {"firstname": "Joe", "sum_salary": 10},
            ],
        )
        self.assertSequenceEqual(
            joes.values("firstname").annotate(sum_salary=Sum("salary")),
            [{"firstname": "Joe", "sum_salary": 12}],
        )

    def test_chained_values_with_expression(self):
        Employee.objects.create(firstname="Joe", lastname="Jones", salary=2)
        joes = Employee.objects.filter(firstname="Joe").values("firstname")
        self.assertSequenceEqual(
            joes.values("firstname", sum_salary=Sum("salary")),
            [{"firstname": "Joe", "sum_salary": 12}],
        )
        self.assertSequenceEqual(
            joes.values(sum_salary=Sum("salary")), [{"sum_salary": 12}]
        )

    def test_values_list_expression(self):
        companies = Company.objects.values_list("name", F("ceo__salary"))
        self.assertCountEqual(
            companies, [("Example Inc.", 10), ("Foobar Ltd.", 20), ("Test GmbH", 30)]
        )

    def test_values_list_expression_flat(self):
        companies = Company.objects.values_list(F("ceo__salary"), flat=True)
        self.assertCountEqual(companies, (10, 20, 30))
