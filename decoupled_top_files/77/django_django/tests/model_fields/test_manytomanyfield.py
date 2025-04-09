"""
The provided Python file contains unit tests for Django's `ManyToManyField` functionality. It includes tests for various scenarios such as handling abstract models, resolving app-relative foreign keys, validating initialization parameters, and testing database table naming conventions. The file defines two test classes:

1. **ManyToManyFieldTests**: Contains tests for:
   - Abstract models and their many-to-many fields.
   - Resolving foreign key relationships in abstract models.
   - Validating the initialization of `ManyToManyField` with valid and invalid types.
   - Ensuring that custom `db_table` specifications are mutually exclusive with intermediary models.

2. **ManyToManyFieldDBTests**: Contains tests for:
   - Retrieving the value of a `ManyToManyField` from
"""
from django.apps import apps
from django.db import models
from django.test import SimpleTestCase, TestCase
from django.test.utils import isolate_apps

from .models import ManyToMany


class ManyToManyFieldTests(SimpleTestCase):

    def test_abstract_model_pending_operations(self):
        """
        Many-to-many fields declared on abstract models should not add lazy
        relations to resolve relationship declared as string (#24215).
        """
        pending_ops_before = list(apps._pending_operations.items())

        class AbstractManyToManyModel(models.Model):
            fk = models.ForeignKey('missing.FK', models.CASCADE)

            class Meta:
                abstract = True

        self.assertIs(AbstractManyToManyModel._meta.apps, apps)
        self.assertEqual(
            pending_ops_before,
            list(apps._pending_operations.items()),
            'Pending lookup added for a many-to-many field on an abstract model'
        )

    @isolate_apps('model_fields', 'model_fields.tests')
    def test_abstract_model_app_relative_foreign_key(self):
        """
        Asserts that the foreign key relationships are correctly resolved when using an abstract model with an app-relative foreign key.
        
        This function tests the resolution of foreign key relationships in Django models when using an abstract base class and app-relative references. It creates models `AbstractReferent`, `Referred`, `Through`, and `ConcreteReferent` within specified app labels ('model_fields' and 'tests') and checks that the `reference` field in `ConcreteReferent` points to the correct `Referred
        """

        class AbstractReferent(models.Model):
            reference = models.ManyToManyField('Referred', through='Through')

            class Meta:
                app_label = 'model_fields'
                abstract = True

        def assert_app_model_resolved(label):
            """
            Asserts that the model references are correctly resolved within a specified application label.
            
            This function checks that the `ConcreteReferent` model's reference field is correctly linked to the `Referred` model through the `Through` model, all within the context of a given application label.
            
            Args:
            label (str): The application label to use for the models.
            
            Functions Used:
            - `Referred`: A model with an application label.
            - `Through`: A model representing the
            """

            class Referred(models.Model):
                class Meta:
                    app_label = label

            class Through(models.Model):
                referred = models.ForeignKey('Referred', on_delete=models.CASCADE)
                referent = models.ForeignKey('ConcreteReferent', on_delete=models.CASCADE)

                class Meta:
                    app_label = label

            class ConcreteReferent(AbstractReferent):
                class Meta:
                    app_label = label

            self.assertEqual(ConcreteReferent._meta.get_field('reference').related_model, Referred)
            self.assertEqual(ConcreteReferent.reference.through, Through)

        assert_app_model_resolved('model_fields')
        assert_app_model_resolved('tests')

    def test_invalid_to_parameter(self):
        """
        Test that an invalid type is raised when initializing a ManyToManyField with an integer.
        
        This function checks if passing an integer as the first argument to
        `ManyToManyField` raises a `TypeError` with a specific error message.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If `ManyToManyField` is initialized with an integer instead of a model, model name, or 'self'.
        
        Example:
        >>> from django.db import models
        """

        msg = (
            "ManyToManyField(1) is invalid. First parameter to "
            "ManyToManyField must be either a model, a model name, or the "
            "string 'self'"
        )
        with self.assertRaisesMessage(TypeError, msg):
            class MyModel(models.Model):
                m2m = models.ManyToManyField(1)

    @isolate_apps('model_fields')
    def test_through_db_table_mutually_exclusive(self):
        """
        Test that specifying a custom `db_table` raises a ValueError when using an intermediary model.
        
        This function creates two models: `Child` and `Through`. The `Through` model serves as an intermediary
        for a many-to-many relationship between instances of `Child`. Attempting to specify a custom `db_table`
        for this relationship results in a `ValueError`, as indicated by the message stored in `msg`.
        
        Args:
        None (This is a test function and does not
        """

        class Child(models.Model):
            pass

        class Through(models.Model):
            referred = models.ForeignKey(Child, on_delete=models.CASCADE)
            referent = models.ForeignKey(Child, on_delete=models.CASCADE)

        msg = 'Cannot specify a db_table if an intermediary model is used.'
        with self.assertRaisesMessage(ValueError, msg):
            class MyModel(models.Model):
                m2m = models.ManyToManyField(
                    Child,
                    through='Through',
                    db_table='custom_name',
                )


class ManyToManyFieldDBTests(TestCase):

    def test_value_from_object_instance_without_pk(self):
        obj = ManyToMany()
        self.assertEqual(obj._meta.get_field('m2m').value_from_object(obj), [])

    def test_value_from_object_instance_with_pk(self):
        """
        Tests the `value_from_object` method of a ManyToMany field on an object instance with a primary key.
        
        This function creates two instances of the `ManyToMany` model, adds a relationship between them, and then checks if the `value_from_object` method correctly returns the related object(s) as a list.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `ManyToMany.objects.create()`: Creates new instances of the `ManyToMany` model
        """

        obj = ManyToMany.objects.create()
        related_obj = ManyToMany.objects.create()
        obj.m2m.add(related_obj)
        self.assertEqual(obj._meta.get_field('m2m').value_from_object(obj), [related_obj])
