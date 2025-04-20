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
        Tests the behavior of an abstract model with an app-relative foreign key relationship.
        
        This function checks that when an abstract model with a ManyToManyField through a related model is defined, and the related model and through model are defined in different apps, the correct models are resolved.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function creates an abstract model `AbstractReferent` with a ManyToManyField to `Referred` through a `Through` model.
        - The `Re
        """

        class AbstractReferent(models.Model):
            reference = models.ManyToManyField('Referred', through='Through')

            class Meta:
                app_label = 'model_fields'
                abstract = True

        def assert_app_model_resolved(label):
            """
            Assert that the model referenced by 'ConcreteReferent' is correctly resolved.
            
            This function checks that the 'reference' field in 'ConcreteReferent' is properly linked to the 'Referred' model and that the intermediate 'Through' model is correctly set as the through model for the many-to-many relationship.
            
            Parameters:
            label (str): The app label used for the models.
            
            Returns:
            None: This function does not return any value. It raises an assertion error if the conditions are not
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
        obj = ManyToMany.objects.create()
        related_obj = ManyToMany.objects.create()
        obj.m2m.add(related_obj)
        self.assertEqual(obj._meta.get_field('m2m').value_from_object(obj), [related_obj])
