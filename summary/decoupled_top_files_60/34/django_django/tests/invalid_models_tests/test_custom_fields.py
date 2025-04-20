from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class CustomFieldTest(SimpleTestCase):

    def test_none_column(self):
        """
        Tests the behavior of a custom AutoField that does not create a database column.
        
        This function verifies that a model with a custom AutoField, which returns None from the db_type method, does not create a corresponding database column. The custom field is named 'field' and maps to 'other_field' in the database, but 'field' itself is not stored in the database.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The `NoColumnField` is a custom Auto
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
