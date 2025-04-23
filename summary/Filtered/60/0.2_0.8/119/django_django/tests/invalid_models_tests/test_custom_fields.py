from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps("invalid_models_tests")
class CustomFieldTest(SimpleTestCase):
    def test_none_column(self):
        """
        Tests the behavior of a custom AutoField that does not create a database column.
        
        This function checks that a model with a custom AutoField, which returns None from its db_type method, does not include the field in its database schema.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Concepts:
        - NoColumnField: A custom AutoField that returns None from its db_type method, indicating no column should be created in the database.
        - Model: A Django model with a field using
        """

        class NoColumnField(models.AutoField):
            def db_type(self, connection):
                # None indicates not to create a column in the database.
                return None

        class Model(models.Model):
            field = NoColumnField(primary_key=True, db_column="other_field")
            other_field = models.IntegerField()

        field = Model._meta.get_field("field")
        self.assertEqual(field.check(), [])
