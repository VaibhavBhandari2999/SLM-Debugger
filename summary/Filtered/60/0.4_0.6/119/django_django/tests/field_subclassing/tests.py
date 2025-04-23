from django.db import connection, models
from django.test import SimpleTestCase

from .fields import CustomDescriptorField, CustomTypedField


class TestDbType(SimpleTestCase):
    def test_db_parameters_respects_db_type(self):
        f = CustomTypedField()
        self.assertEqual(f.db_parameters(connection)["type"], "custom_field")


class DescriptorClassTest(SimpleTestCase):
    def test_descriptor_class(self):
        """
        Tests the behavior of a custom descriptor field in a Django model.
        
        This function creates an instance of a model with a custom descriptor field and tests the behavior of the field during attribute setting and retrieval. The key parameters include the model and the field. The function checks the counts of attribute get and set operations and ensures the correct values are returned.
        
        Parameters:
        None (the function is a test method and does not take any parameters)
        
        Returns:
        None (the function asserts the expected behavior through internal checks
        """

        class CustomDescriptorModel(models.Model):
            name = CustomDescriptorField(max_length=32)

        m = CustomDescriptorModel()
        self.assertFalse(hasattr(m, "_name_get_count"))
        # The field is set to its default in the model constructor.
        self.assertEqual(m._name_set_count, 1)
        m.name = "foo"
        self.assertFalse(hasattr(m, "_name_get_count"))
        self.assertEqual(m._name_set_count, 2)
        self.assertEqual(m.name, "foo")
        self.assertEqual(m._name_get_count, 1)
        self.assertEqual(m._name_set_count, 2)
        m.name = "bar"
        self.assertEqual(m._name_get_count, 1)
        self.assertEqual(m._name_set_count, 3)
        self.assertEqual(m.name, "bar")
        self.assertEqual(m._name_get_count, 2)
        self.assertEqual(m._name_set_count, 3)
