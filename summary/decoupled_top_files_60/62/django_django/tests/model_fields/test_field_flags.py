from django import test
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation,
)
from django.db import models

from .models import AllFieldsModel

NON_CONCRETE_FIELDS = (
    models.ForeignObject,
    GenericForeignKey,
    GenericRelation,
)

NON_EDITABLE_FIELDS = (
    models.BinaryField,
    GenericForeignKey,
    GenericRelation,
)

RELATION_FIELDS = (
    models.ForeignKey,
    models.ForeignObject,
    models.ManyToManyField,
    models.OneToOneField,
    GenericForeignKey,
    GenericRelation,
)

MANY_TO_MANY_CLASSES = {
    models.ManyToManyField,
}

MANY_TO_ONE_CLASSES = {
    models.ForeignObject,
    models.ForeignKey,
    GenericForeignKey,
}

ONE_TO_MANY_CLASSES = {
    models.ForeignObjectRel,
    models.ManyToOneRel,
    GenericRelation,
}

ONE_TO_ONE_CLASSES = {
    models.OneToOneField,
}

FLAG_PROPERTIES = (
    'concrete',
    'editable',
    'is_relation',
    'model',
    'hidden',
    'one_to_many',
    'many_to_one',
    'many_to_many',
    'one_to_one',
    'related_model',
)

FLAG_PROPERTIES_FOR_RELATIONS = (
    'one_to_many',
    'many_to_one',
    'many_to_many',
    'one_to_one',
)


class FieldFlagsTests(test.SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        """
        Sets up class-level attributes for testing an AllFieldsModel.
        
        This method is called once before any tests in the class are run. It initializes several class-level attributes that are used to test the fields of the AllFieldsModel.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes Set:
        - `cls.fields`: A list of all fields in the model, including private fields.
        - `cls.all_fields`: A list of all fields and many-to-many relationships in the model, including private
        """

        super().setUpClass()
        cls.fields = [
            *AllFieldsModel._meta.fields,
            *AllFieldsModel._meta.private_fields,
        ]

        cls.all_fields = [
            *cls.fields,
            *AllFieldsModel._meta.many_to_many,
            *AllFieldsModel._meta.private_fields,
        ]

        cls.fields_and_reverse_objects = [
            *cls.all_fields,
            *AllFieldsModel._meta.related_objects,
        ]

    def test_each_field_should_have_a_concrete_attribute(self):
        self.assertTrue(all(f.concrete.__class__ == bool for f in self.fields))

    def test_each_field_should_have_an_editable_attribute(self):
        self.assertTrue(all(f.editable.__class__ == bool for f in self.all_fields))

    def test_each_field_should_have_a_has_rel_attribute(self):
        self.assertTrue(all(f.is_relation.__class__ == bool for f in self.all_fields))

    def test_each_object_should_have_auto_created(self):
        self.assertTrue(
            all(f.auto_created.__class__ == bool for f in self.fields_and_reverse_objects)
        )

    def test_non_concrete_fields(self):
        for field in self.fields:
            if type(field) in NON_CONCRETE_FIELDS:
                self.assertFalse(field.concrete)
            else:
                self.assertTrue(field.concrete)

    def test_non_editable_fields(self):
        """
        Tests the editable status of fields in a model.
        
        This function iterates through all fields in the model and checks if they are editable. It uses a predefined list of non-editable fields (NON_EDITABLE_FIELDS) to determine which fields should not be editable. For each field, it verifies that non-editable fields are marked as not editable and that other fields are marked as editable.
        
        Parameters:
        self: The instance of the test class.
        
        Returns:
        None: This function does not return any
        """

        for field in self.all_fields:
            if type(field) in NON_EDITABLE_FIELDS:
                self.assertFalse(field.editable)
            else:
                self.assertTrue(field.editable)

    def test_related_fields(self):
        for field in self.all_fields:
            if type(field) in RELATION_FIELDS:
                self.assertTrue(field.is_relation)
            else:
                self.assertFalse(field.is_relation)

    def test_field_names_should_always_be_available(self):
        for field in self.fields_and_reverse_objects:
            self.assertTrue(field.name)

    def test_all_field_types_should_have_flags(self):
        for field in self.fields_and_reverse_objects:
            for flag in FLAG_PROPERTIES:
                self.assertTrue(hasattr(field, flag), "Field %s does not have flag %s" % (field, flag))
            if field.is_relation:
                true_cardinality_flags = sum(
                    getattr(field, flag) is True
                    for flag in FLAG_PROPERTIES_FOR_RELATIONS
                )
                # If the field has a relation, there should be only one of the
                # 4 cardinality flags available.
                self.assertEqual(1, true_cardinality_flags)

    def test_cardinality_m2m(self):
        """
        Tests the cardinality of many-to-many fields in a Django model.
        
        This function checks the many-to-many fields in a Django model to ensure they are of the expected type and that their reverse relationships are also many-to-many. It returns nothing but asserts the conditions.
        
        Parameters:
        self: The instance of the test case class.
        
        Returns:
        None
        
        Key Points:
        - Identifies many-to-many fields in the model.
        - Verifies that the reverse relationships of these fields are also many-to-many
        """

        m2m_type_fields = [
            f for f in self.all_fields
            if f.is_relation and f.many_to_many
        ]
        # Test classes are what we expect
        self.assertEqual(MANY_TO_MANY_CLASSES, {f.__class__ for f in m2m_type_fields})

        # Ensure all m2m reverses are m2m
        for field in m2m_type_fields:
            reverse_field = field.remote_field
            self.assertTrue(reverse_field.is_relation)
            self.assertTrue(reverse_field.many_to_many)
            self.assertTrue(reverse_field.related_model)

    def test_cardinality_o2m(self):
        """
        Tests the cardinality of one-to-many (o2m) relationships in the model fields.
        
        This function checks the following:
        1. It filters the fields and their reverse objects to find all one-to-many (o2m) relationships.
        2. It verifies that the classes of these fields match the expected classes specified in `ONE_TO_MANY_CLASSES`.
        3. It ensures that all one-to-many fields have corresponding many-to-one (m2o) reverse fields.
        
        Parameters:
        self: The current
        """

        o2m_type_fields = [
            f for f in self.fields_and_reverse_objects
            if f.is_relation and f.one_to_many
        ]
        # Test classes are what we expect
        self.assertEqual(ONE_TO_MANY_CLASSES, {f.__class__ for f in o2m_type_fields})

        # Ensure all o2m reverses are m2o
        for field in o2m_type_fields:
            if field.concrete:
                reverse_field = field.remote_field
                self.assertTrue(reverse_field.is_relation and reverse_field.many_to_one)

    def test_cardinality_m2o(self):
        """
        Tests the cardinality of many-to-one fields in a model.
        
        This function checks the cardinality of fields that are many-to-one (m2o) relationships in a model. It ensures that the fields are of the expected type and that their reverse relationships are one-to-many (o2m).
        
        Key Parameters:
        - self: The test case instance.
        
        Returns:
        - None: This function does not return any value. It performs assertions to validate the model fields.
        
        Key Assertions:
        1. The set
        """

        m2o_type_fields = [
            f for f in self.fields_and_reverse_objects
            if f.is_relation and f.many_to_one
        ]
        # Test classes are what we expect
        self.assertEqual(MANY_TO_ONE_CLASSES, {f.__class__ for f in m2o_type_fields})

        # Ensure all m2o reverses are o2m
        for obj in m2o_type_fields:
            if hasattr(obj, 'field'):
                reverse_field = obj.field
                self.assertTrue(reverse_field.is_relation and reverse_field.one_to_many)

    def test_cardinality_o2o(self):
        o2o_type_fields = [
            f for f in self.all_fields
            if f.is_relation and f.one_to_one
        ]
        # Test classes are what we expect
        self.assertEqual(ONE_TO_ONE_CLASSES, {f.__class__ for f in o2o_type_fields})

        # Ensure all o2o reverses are o2o
        for obj in o2o_type_fields:
            if hasattr(obj, 'field'):
                reverse_field = obj.field
                self.assertTrue(reverse_field.is_relation and reverse_field.one_to_one)

    def test_hidden_flag(self):
        incl_hidden = set(AllFieldsModel._meta.get_fields(include_hidden=True))
        no_hidden = set(AllFieldsModel._meta.get_fields())
        fields_that_should_be_hidden = (incl_hidden - no_hidden)
        for f in incl_hidden:
            self.assertEqual(f in fields_that_should_be_hidden, f.hidden)

    def test_model_and_reverse_model_should_equal_on_relations(self):
        for field in AllFieldsModel._meta.get_fields():
            is_concrete_forward_field = field.concrete and field.related_model
            if is_concrete_forward_field:
                reverse_field = field.remote_field
                self.assertEqual(field.model, reverse_field.related_model)
                self.assertEqual(field.related_model, reverse_field.model)

    def test_null(self):
        """
        Test the null attribute for specific fields in the model.
        
        This function checks the null attribute for the 'm2m' and 'reverse2' fields in the 'AllFieldsModel' model. It ensures that the 'm2m' field is not nullable, while the 'reverse2' field is nullable. The function does not take any parameters and does not return any value.
        """

        # null isn't well defined for a ManyToManyField, but changing it to
        # True causes backwards compatibility problems (#25320).
        self.assertFalse(AllFieldsModel._meta.get_field('m2m').null)
        self.assertTrue(AllFieldsModel._meta.get_field('reverse2').null)
