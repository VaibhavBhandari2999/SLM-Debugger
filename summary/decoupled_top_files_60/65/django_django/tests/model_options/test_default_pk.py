from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test import SimpleTestCase, override_settings
from django.test.utils import isolate_apps


@isolate_apps('model_options')
class TestDefaultPK(SimpleTestCase):
    @override_settings(DEFAULT_AUTO_FIELD='django.db.models.NonexistentAutoField')
    def test_default_auto_field_setting_nonexistent(self):
        """
        Test the default auto field setting when a nonexistent field is referenced.
        
        This test checks for an `ImproperlyConfigured` exception when the `DEFAULT_AUTO_FIELD`
        setting refers to a non-existent field, specifically 'django.db.models.NonexistentAutoField'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ImproperlyConfigured: If the specified auto field cannot be imported.
        
        Usage:
        This test function is used to ensure that the application correctly handles
        the case where a
        """

        msg = (
            "DEFAULT_AUTO_FIELD refers to the module "
            "'django.db.models.NonexistentAutoField' that could not be "
            "imported."
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            class Model(models.Model):
                pass

    @isolate_apps('model_options.apps.ModelPKNonexistentConfig')
    def test_app_default_auto_field_nonexistent(self):
        """
        Test for the default_auto_field setting in an app configuration.
        
        This test checks if the `default_auto_field` setting in the app configuration
        raises an `ImproperlyConfigured` exception when it refers to a non-existent
        auto field. The test creates a model and expects an import error due to a
        non-existent auto field.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ImproperlyConfigured: If the `default_auto_field` setting is correctly
        configured
        """

        msg = (
            "model_options.apps.ModelPKNonexistentConfig.default_auto_field "
            "refers to the module 'django.db.models.NonexistentAutoField' "
            "that could not be imported."
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            class Model(models.Model):
                pass

    @override_settings(DEFAULT_AUTO_FIELD='django.db.models.TextField')
    def test_default_auto_field_setting_non_auto(self):
        msg = (
            "Primary key 'django.db.models.TextField' referred by "
            "DEFAULT_AUTO_FIELD must subclass AutoField."
        )
        with self.assertRaisesMessage(ValueError, msg):
            class Model(models.Model):
                pass

    @isolate_apps('model_options.apps.ModelPKNonAutoConfig')
    def test_app_default_auto_field_non_auto(self):
        """
        Test the default auto field functionality for a model.
        
        This function checks if a model with a primary key of type `TextField` and no specified `AutoField` or `BigAutoField` raises a `ValueError`. The error message should indicate that the primary key must subclass `AutoField`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the primary key type is `TextField` and no `AutoField` or `BigAutoField` is specified.
        
        Example:
        """

        msg = (
            "Primary key 'django.db.models.TextField' referred by "
            "model_options.apps.ModelPKNonAutoConfig.default_auto_field must "
            "subclass AutoField."
        )
        with self.assertRaisesMessage(ValueError, msg):
            class Model(models.Model):
                pass

    @override_settings(DEFAULT_AUTO_FIELD=None)
    def test_default_auto_field_setting_none(self):
        msg = 'DEFAULT_AUTO_FIELD must not be empty.'
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            class Model(models.Model):
                pass

    @isolate_apps('model_options.apps.ModelPKNoneConfig')
    def test_app_default_auto_field_none(self):
        msg = (
            'model_options.apps.ModelPKNoneConfig.default_auto_field must not '
            'be empty.'
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            class Model(models.Model):
                pass

    @isolate_apps('model_options.apps.ModelDefaultPKConfig')
    @override_settings(DEFAULT_AUTO_FIELD='django.db.models.SmallAutoField')
    def test_default_auto_field_setting(self):
        """
        Tests the default setting for the primary key field in a Django model. By default, the primary key field is an instance of models.SmallAutoField. This test verifies that the model created without specifying a primary key field automatically receives this type of field.
        
        Parameters:
        None
        
        Returns:
        None
        """

        class Model(models.Model):
            pass

        self.assertIsInstance(Model._meta.pk, models.SmallAutoField)

    @isolate_apps('model_options.apps.ModelPKConfig')
    @override_settings(DEFAULT_AUTO_FIELD='django.db.models.AutoField')
    def test_app_default_auto_field(self):
        class Model(models.Model):
            pass

        self.assertIsInstance(Model._meta.pk, models.SmallAutoField)

    @isolate_apps('model_options.apps.ModelDefaultPKConfig')
    @override_settings(DEFAULT_AUTO_FIELD='django.db.models.SmallAutoField')
    def test_m2m_default_auto_field_setting(self):
        class M2MModel(models.Model):
            m2m = models.ManyToManyField('self')

        m2m_pk = M2MModel._meta.get_field('m2m').remote_field.through._meta.pk
        self.assertIsInstance(m2m_pk, models.SmallAutoField)

    @isolate_apps('model_options.apps.ModelPKConfig')
    @override_settings(DEFAULT_AUTO_FIELD='django.db.models.AutoField')
    def test_m2m_app_default_auto_field(self):
        class M2MModel(models.Model):
            m2m = models.ManyToManyField('self')

        m2m_pk = M2MModel._meta.get_field('m2m').remote_field.through._meta.pk
        self.assertIsInstance(m2m_pk, models.SmallAutoField)
 
):
            m2m = models.ManyToManyField('self')

        m2m_pk = M2MModel._meta.get_field('m2m').remote_field.through._meta.pk
        self.assertIsInstance(m2m_pk, models.SmallAutoField)
