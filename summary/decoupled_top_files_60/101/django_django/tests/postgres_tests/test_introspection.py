from io import StringIO

from django.core.management import call_command
from django.test.utils import modify_settings

from . import PostgreSQLTestCase


@modify_settings(INSTALLED_APPS={"append": "django.contrib.postgres"})
class InspectDBTests(PostgreSQLTestCase):
    def assertFieldsInModel(self, model, field_outputs):
        """
        Assert that specific fields are present in the model's inspectdb output.
        
        This function checks if the specified fields are included in the output of the `inspectdb` command for a given model.
        
        Parameters:
        model (str): The name of the model to inspect.
        field_outputs (list): A list of strings representing the expected field outputs.
        
        Returns:
        None: This function does not return anything. It raises an assertion error if the fields are not found in the output.
        
        Usage:
        assert
        """

        out = StringIO()
        call_command(
            "inspectdb",
            table_name_filter=lambda tn: tn.startswith(model),
            stdout=out,
        )
        output = out.getvalue()
        for field_output in field_outputs:
            self.assertIn(field_output, output)

    def test_range_fields(self):
        self.assertFieldsInModel(
            "postgres_tests_rangesmodel",
            [
                "ints = django.contrib.postgres.fields.IntegerRangeField(blank=True, "
                "null=True)",
                "bigints = django.contrib.postgres.fields.BigIntegerRangeField("
                "blank=True, null=True)",
                "decimals = django.contrib.postgres.fields.DecimalRangeField("
                "blank=True, null=True)",
                "timestamps = django.contrib.postgres.fields.DateTimeRangeField("
                "blank=True, null=True)",
                "dates = django.contrib.postgres.fields.DateRangeField(blank=True, "
                "null=True)",
            ],
        )
