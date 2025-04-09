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
