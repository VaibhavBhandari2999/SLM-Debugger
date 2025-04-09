from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class CustomFieldTest(SimpleTestCase):

    def test_none_column(self):
        """
        Tests the behavior of a custom AutoField that does not create a corresponding database column.
        
        This function verifies that when using a `NoColumnField` as a primary key in a Django model,
        the field is correctly identified as not requiring a database column. The `db_type` method
        of `NoColumnField` returns `None`, indicating no column should be created. The test checks
        that the `check` method on the field returns an empty list, signifying no issues
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
