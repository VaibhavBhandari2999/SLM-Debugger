from decimal import Decimal

from django.apps import apps
from django.core import checks
from django.core.exceptions import FieldError
from django.db import models
from django.test import TestCase, skipIfDBFeature
from django.test.utils import isolate_apps

from .models import Bar, FkToChar, Foo, PrimaryKeyCharModel


class ForeignKeyTests(TestCase):

    def test_callable_default(self):
        """A lazy callable may be used for ForeignKey.default."""
        a = Foo.objects.create(id=1, a='abc', d=Decimal('12.34'))
        b = Bar.objects.create(b='bcd')
        self.assertEqual(b.a, a)

    @skipIfDBFeature('interprets_empty_strings_as_nulls')
    def test_empty_string_fk(self):
        """
        Empty strings foreign key values don't get converted to None (#19299).
        """
        char_model_empty = PrimaryKeyCharModel.objects.create(string='')
        fk_model_empty = FkToChar.objects.create(out=char_model_empty)
        fk_model_empty = FkToChar.objects.select_related('out').get(id=fk_model_empty.pk)
        self.assertEqual(fk_model_empty.out, char_model_empty)

    @isolate_apps('model_fields')
    def test_warning_when_unique_true_on_fk(self):
        """
        Tests the warning behavior when unique=True is set on a ForeignKey.
        
        This function creates a Django model with a ForeignKey field set to unique=True. It then checks the model for warnings and asserts that the expected warning is raised. The warning indicates that setting unique=True on a ForeignKey is equivalent to using a OneToOneField and suggests using the latter instead.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Expected Output:
        - A warning is generated, indicating that setting unique=True on a ForeignKey is equivalent to using
        """

        class Foo(models.Model):
            pass

        class FKUniqueTrue(models.Model):
            fk_field = models.ForeignKey(Foo, models.CASCADE, unique=True)

        model = FKUniqueTrue()
        expected_warnings = [
            checks.Warning(
                'Setting unique=True on a ForeignKey has the same effect as using a OneToOneField.',
                hint='ForeignKey(unique=True) is usually better served by a OneToOneField.',
                obj=FKUniqueTrue.fk_field.field,
                id='fields.W342',
            )
        ]
        warnings = model.check()
        self.assertEqual(warnings, expected_warnings)

    def test_related_name_converted_to_text(self):
        rel_name = Bar._meta.get_field('a').remote_field.related_name
        self.assertIsInstance(rel_name, str)

    def test_abstract_model_pending_operations(self):
        """
        Foreign key fields declared on abstract models should not add lazy
        relations to resolve relationship declared as string (#24215).
        """
        pending_ops_before = list(apps._pending_operations.items())

        class AbstractForeignKeyModel(models.Model):
            fk = models.ForeignKey('missing.FK', models.CASCADE)

            class Meta:
                abstract = True

        self.assertIs(AbstractForeignKeyModel._meta.apps, apps)
        self.assertEqual(
            pending_ops_before,
            list(apps._pending_operations.items()),
            'Pending lookup added for a foreign key on an abstract model'
        )

    @isolate_apps('model_fields', 'model_fields.tests')
    def test_abstract_model_app_relative_foreign_key(self):
        class AbstractReferent(models.Model):
            reference = models.ForeignKey('Referred', on_delete=models.CASCADE)

            class Meta:
                app_label = 'model_fields'
                abstract = True

        def assert_app_model_resolved(label):
            class Referred(models.Model):
                class Meta:
                    app_label = label

            class ConcreteReferent(AbstractReferent):
                class Meta:
                    app_label = label

            self.assertEqual(ConcreteReferent._meta.get_field('reference').related_model, Referred)

        assert_app_model_resolved('model_fields')
        assert_app_model_resolved('tests')

    @isolate_apps('model_fields')
    def test_to_python(self):
        class Foo(models.Model):
            pass

        class Bar(models.Model):
            fk = models.ForeignKey(Foo, models.CASCADE)

        self.assertEqual(Bar._meta.get_field('fk').to_python('1'), 1)

    @isolate_apps('model_fields')
    def test_fk_to_fk_get_col_output_field(self):
        """
        Tests the output field of a ForeignKey to a ForeignKey.
        
        This function verifies that the output field of a ForeignKey to another ForeignKey correctly returns the primary key field of the target model.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Concepts:
        - ForeignKey: A field that represents a relationship to another model.
        - Primary Key: A unique identifier for each record in a model.
        - Alias: An alias for a table or field in a database query.
        
        Tested Scenario:
        - A
        """

        class Foo(models.Model):
            pass

        class Bar(models.Model):
            foo = models.ForeignKey(Foo, models.CASCADE, primary_key=True)

        class Baz(models.Model):
            bar = models.ForeignKey(Bar, models.CASCADE, primary_key=True)

        col = Baz._meta.get_field('bar').get_col('alias')
        self.assertIs(col.output_field, Foo._meta.pk)

    @isolate_apps('model_fields')
    def test_recursive_fks_get_col(self):
        class Foo(models.Model):
            bar = models.ForeignKey('Bar', models.CASCADE, primary_key=True)

        class Bar(models.Model):
            foo = models.ForeignKey(Foo, models.CASCADE, primary_key=True)

        with self.assertRaisesMessage(ValueError, 'Cannot resolve output_field'):
            Foo._meta.get_field('bar').get_col('alias')

    @isolate_apps('model_fields')
    def test_non_local_to_field(self):
        """
        Test for non-local field reference in a ForeignKey.
        
        This function checks for a ForeignKey that references a field ('key') which is not local to the model ('Child'). The function creates three models: 'Parent', 'Child', and 'Related'. 'Parent' and 'Child' are related through inheritance, and 'Related' has a ForeignKey to 'Child' with 'key' as the to_field. The function asserts that a FieldError is raised when trying to access the related fields of 'child
        """

        class Parent(models.Model):
            key = models.IntegerField(unique=True)

        class Child(Parent):
            pass

        class Related(models.Model):
            child = models.ForeignKey(Child, on_delete=models.CASCADE, to_field='key')

        msg = (
            "'model_fields.Related.child' refers to field 'key' which is not "
            "local to model 'model_fields.Child'."
        )
        with self.assertRaisesMessage(FieldError, msg):
            Related._meta.get_field('child').related_fields
