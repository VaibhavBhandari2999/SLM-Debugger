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
        a = Foo.objects.create(id=1, a="abc", d=Decimal("12.34"))
        b = Bar.objects.create(b="bcd")
        self.assertEqual(b.a, a)

    @skipIfDBFeature("interprets_empty_strings_as_nulls")
    def test_empty_string_fk(self):
        """
        Empty strings foreign key values don't get converted to None (#19299).
        """
        char_model_empty = PrimaryKeyCharModel.objects.create(string="")
        fk_model_empty = FkToChar.objects.create(out=char_model_empty)
        fk_model_empty = FkToChar.objects.select_related("out").get(
            id=fk_model_empty.pk
        )
        self.assertEqual(fk_model_empty.out, char_model_empty)

    @isolate_apps("model_fields")
    def test_warning_when_unique_true_on_fk(self):
        """
        Tests the warning behavior when unique=True is set on a ForeignKey.
        
        This function creates a Django model with a ForeignKey field configured to be unique. It then checks the model for warnings and ensures that the expected warning is raised. The warning indicates that setting unique=True on a ForeignKey is equivalent to using a OneToOneField and suggests using the latter.
        
        Parameters:
        None
        
        Returns:
        None
        
        Expected Output:
        A list of warnings, containing a single Warning object with the following attributes:
        - level
        """

        class Foo(models.Model):
            pass

        class FKUniqueTrue(models.Model):
            fk_field = models.ForeignKey(Foo, models.CASCADE, unique=True)

        model = FKUniqueTrue()
        expected_warnings = [
            checks.Warning(
                "Setting unique=True on a ForeignKey has the same effect as using a "
                "OneToOneField.",
                hint=(
                    "ForeignKey(unique=True) is usually better served by a "
                    "OneToOneField."
                ),
                obj=FKUniqueTrue.fk_field.field,
                id="fields.W342",
            )
        ]
        warnings = model.check()
        self.assertEqual(warnings, expected_warnings)

    def test_related_name_converted_to_text(self):
        rel_name = Bar._meta.get_field("a").remote_field.related_name
        self.assertIsInstance(rel_name, str)

    def test_abstract_model_pending_operations(self):
        """
        Foreign key fields declared on abstract models should not add lazy
        relations to resolve relationship declared as string (#24215).
        """
        pending_ops_before = list(apps._pending_operations.items())

        class AbstractForeignKeyModel(models.Model):
            fk = models.ForeignKey("missing.FK", models.CASCADE)

            class Meta:
                abstract = True

        self.assertIs(AbstractForeignKeyModel._meta.apps, apps)
        self.assertEqual(
            pending_ops_before,
            list(apps._pending_operations.items()),
            "Pending lookup added for a foreign key on an abstract model",
        )

    @isolate_apps("model_fields", "model_fields.tests")
    def test_abstract_model_app_relative_foreign_key(self):
        class AbstractReferent(models.Model):
            reference = models.ForeignKey("Referred", on_delete=models.CASCADE)

            class Meta:
                app_label = "model_fields"
                abstract = True

        def assert_app_model_resolved(label):
            class Referred(models.Model):
                class Meta:
                    app_label = label

            class ConcreteReferent(AbstractReferent):
                class Meta:
                    app_label = label

            self.assertEqual(
                ConcreteReferent._meta.get_field("reference").related_model, Referred
            )

        assert_app_model_resolved("model_fields")
        assert_app_model_resolved("tests")

    @isolate_apps("model_fields")
    def test_to_python(self):
        class Foo(models.Model):
            pass

        class Bar(models.Model):
            fk = models.ForeignKey(Foo, models.CASCADE)

        self.assertEqual(Bar._meta.get_field("fk").to_python("1"), 1)

    @isolate_apps("model_fields")
    def test_fk_to_fk_get_col_output_field(self):
        class Foo(models.Model):
            pass

        class Bar(models.Model):
            foo = models.ForeignKey(Foo, models.CASCADE, primary_key=True)

        class Baz(models.Model):
            bar = models.ForeignKey(Bar, models.CASCADE, primary_key=True)

        col = Baz._meta.get_field("bar").get_col("alias")
        self.assertIs(col.output_field, Foo._meta.pk)

    @isolate_apps("model_fields")
    def test_recursive_fks_get_col(self):
        """
        Tests the recursive ForeignKey resolution in the get_col method.
        
        This function checks the behavior of the get_col method when dealing with recursive ForeignKey relationships. It creates two models, Foo and Bar, each having a ForeignKey to the other, forming a recursive relationship. The primary key of each model is set to be the ForeignKey to the other model.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the get_col method cannot resolve the output field for the recursive ForeignKey relationship.
        
        Note:
        """

        class Foo(models.Model):
            bar = models.ForeignKey("Bar", models.CASCADE, primary_key=True)

        class Bar(models.Model):
            foo = models.ForeignKey(Foo, models.CASCADE, primary_key=True)

        with self.assertRaisesMessage(ValueError, "Cannot resolve output_field"):
            Foo._meta.get_field("bar").get_col("alias")

    @isolate_apps("model_fields")
    def test_non_local_to_field(self):
        class Parent(models.Model):
            key = models.IntegerField(unique=True)

        class Child(Parent):
            pass

        class Related(models.Model):
            child = models.ForeignKey(Child, on_delete=models.CASCADE, to_field="key")

        msg = (
            "'model_fields.Related.child' refers to field 'key' which is not "
            "local to model 'model_fields.Child'."
        )
        with self.assertRaisesMessage(FieldError, msg):
            Related._meta.get_field("child").related_fields

    def test_invalid_to_parameter(self):
        """
        Tests the validation of an invalid ForeignKey parameter.
        
        This function checks if a `ForeignKey` with an invalid first parameter raises a `TypeError` with the expected error message. The first parameter to `ForeignKey` must be either a model, a model name, or the string 'self'. If an integer is passed, a specific error message is expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If the `ForeignKey` is instantiated with an invalid first parameter, a `TypeError
        """

        msg = (
            "ForeignKey(1) is invalid. First parameter to ForeignKey must be "
            "either a model, a model name, or the string 'self'"
        )
        with self.assertRaisesMessage(TypeError, msg):

            class MyModel(models.Model):
                child = models.ForeignKey(1, models.CASCADE)

    def test_manager_class_getitem(self):
        self.assertIs(models.ForeignKey["Foo"], models.ForeignKey)
