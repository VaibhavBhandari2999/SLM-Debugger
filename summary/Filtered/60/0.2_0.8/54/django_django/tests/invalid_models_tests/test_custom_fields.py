from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class CustomFieldTest(SimpleTestCase):

    def test_none_column(self):
        """
        Tests the behavior of a custom AutoField that does not create a corresponding database column.
        
        This function checks the behavior of a custom AutoField named `NoColumnField` which returns `None` from its `db_type` method, indicating that no column should be created for this field in the database. The test involves creating a Django model with such a field and another integer field. The function then retrieves the field from the model's metadata and checks if the field's validation checks return an empty list,
        """

        class NoColumnField(models.AutoField):
            def db_type(self, connection):
                # None indicates not to create a column in the database.
                return None

        class Model(models.Model):
            field = NoColumnField(primary_key=True, db_column="other_field")
            other_field = models.IntegerField()

        field = Model._meta.get_field('field')
        self.assertEqual(field.check(), [])
