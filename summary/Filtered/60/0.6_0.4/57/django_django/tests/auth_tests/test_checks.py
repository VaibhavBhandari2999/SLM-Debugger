from django.contrib.auth.checks import (
    check_models_permissions, check_user_model,
)
from django.contrib.auth.models import AbstractBaseUser
from django.core import checks
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.test import (
    SimpleTestCase, override_settings, override_system_checks,
)
from django.test.utils import isolate_apps

from .models import CustomUserNonUniqueUsername


@isolate_apps('auth_tests', attr_name='apps')
@override_system_checks([check_user_model])
class UserModelChecksTests(SimpleTestCase):
    @override_settings(AUTH_USER_MODEL='auth_tests.CustomUserNonListRequiredFields')
    def test_required_fields_is_list(self):
        """REQUIRED_FIELDS should be a list."""
        class CustomUserNonListRequiredFields(AbstractBaseUser):
            username = models.CharField(max_length=30, unique=True)
            date_of_birth = models.DateField()

            USERNAME_FIELD = 'username'
            REQUIRED_FIELDS = 'date_of_birth'

        errors = checks.run_checks(app_configs=self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Error(
                "'REQUIRED_FIELDS' must be a list or tuple.",
                obj=CustomUserNonListRequiredFields,
                id='auth.E001',
            ),
        ])

    @override_settings(AUTH_USER_MODEL='auth_tests.CustomUserBadRequiredFields')
    def test_username_not_in_required_fields(self):
        """USERNAME_FIELD should not appear in REQUIRED_FIELDS."""
        class CustomUserBadRequiredFields(AbstractBaseUser):
            username = models.CharField(max_length=30, unique=True)
            date_of_birth = models.DateField()

            USERNAME_FIELD = 'username'
            REQUIRED_FIELDS = ['username', 'date_of_birth']

        errors = checks.run_checks(self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Error(
                "The field named as the 'USERNAME_FIELD' for a custom user model "
                "must not be included in 'REQUIRED_FIELDS'.",
                hint=(
                    "The 'USERNAME_FIELD' is currently set to 'username', you "
                    "should remove 'username' from the 'REQUIRED_FIELDS'."
                ),
                obj=CustomUserBadRequiredFields,
                id='auth.E002',
            ),
        ])

    @override_settings(AUTH_USER_MODEL='auth_tests.CustomUserNonUniqueUsername')
    def test_username_non_unique(self):
        """
        A non-unique USERNAME_FIELD raises an error only if the default
        authentication backend is used. Otherwise, a warning is raised.
        """
        errors = checks.run_checks()
        self.assertEqual(errors, [
            checks.Error(
                "'CustomUserNonUniqueUsername.username' must be "
                "unique because it is named as the 'USERNAME_FIELD'.",
                obj=CustomUserNonUniqueUsername,
                id='auth.E003',
            ),
        ])
        with self.settings(AUTHENTICATION_BACKENDS=['my.custom.backend']):
            errors = checks.run_checks()
            self.assertEqual(errors, [
                checks.Warning(
                    "'CustomUserNonUniqueUsername.username' is named as "
                    "the 'USERNAME_FIELD', but it is not unique.",
                    hint='Ensure that your authentication backend(s) can handle non-unique usernames.',
                    obj=CustomUserNonUniqueUsername,
                    id='auth.W004',
                ),
            ])

    @override_settings(AUTH_USER_MODEL='auth_tests.CustomUserPartiallyUnique')
    def test_username_partially_unique(self):
        """
        Tests the behavior of a custom user model with a partially unique username field.
        
        This function checks the behavior of a custom user model that has a partially unique username field. It creates a custom user model `CustomUserPartiallyUnique` with a `username` field and a unique constraint that only applies when the `password` field is not null. The function runs Django's model checks to verify the behavior of this custom model.
        
        Parameters:
        - `self`: The test case instance.
        
        Returns:
        - None
        """

        class CustomUserPartiallyUnique(AbstractBaseUser):
            username = models.CharField(max_length=30)
            USERNAME_FIELD = 'username'

            class Meta:
                constraints = [
                    UniqueConstraint(
                        fields=['username'],
                        name='partial_username_unique',
                        condition=Q(password__isnull=False),
                    ),
                ]

        errors = checks.run_checks(app_configs=self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Error(
                "'CustomUserPartiallyUnique.username' must be unique because "
                "it is named as the 'USERNAME_FIELD'.",
                obj=CustomUserPartiallyUnique,
                id='auth.E003',
            ),
        ])
        with self.settings(AUTHENTICATION_BACKENDS=['my.custom.backend']):
            errors = checks.run_checks(app_configs=self.apps.get_app_configs())
            self.assertEqual(errors, [
                checks.Warning(
                    "'CustomUserPartiallyUnique.username' is named as the "
                    "'USERNAME_FIELD', but it is not unique.",
                    hint=(
                        'Ensure that your authentication backend(s) can '
                        'handle non-unique usernames.'
                    ),
                    obj=CustomUserPartiallyUnique,
                    id='auth.W004',
                ),
            ])

    @override_settings(AUTH_USER_MODEL='auth_tests.CustomUserUniqueConstraint')
    def test_username_unique_with_model_constraint(self):
        class CustomUserUniqueConstraint(AbstractBaseUser):
            username = models.CharField(max_length=30)
            USERNAME_FIELD = 'username'

            class Meta:
                constraints = [
                    UniqueConstraint(fields=['username'], name='username_unique'),
                ]

        self.assertEqual(checks.run_checks(app_configs=self.apps.get_app_configs()), [])
        with self.settings(AUTHENTICATION_BACKENDS=['my.custom.backend']):
            errors = checks.run_checks(app_configs=self.apps.get_app_configs())
            self.assertEqual(errors, [])

    @override_settings(AUTH_USER_MODEL='auth_tests.BadUser')
    def test_is_anonymous_authenticated_methods(self):
        """
        <User Model>.is_anonymous/is_authenticated must not be methods.
        """
        class BadUser(AbstractBaseUser):
            username = models.CharField(max_length=30, unique=True)
            USERNAME_FIELD = 'username'

            def is_anonymous(self):
                return True

            def is_authenticated(self):
                return True

        errors = checks.run_checks(app_configs=self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Critical(
                '%s.is_anonymous must be an attribute or property rather than '
                'a method. Ignoring this is a security issue as anonymous '
                'users will be treated as authenticated!' % BadUser,
                obj=BadUser,
                id='auth.C009',
            ),
            checks.Critical(
                '%s.is_authenticated must be an attribute or property rather '
                'than a method. Ignoring this is a security issue as anonymous '
                'users will be treated as authenticated!' % BadUser,
                obj=BadUser,
                id='auth.C010',
            ),
        ])


@isolate_apps('auth_tests', attr_name='apps')
@override_system_checks([check_models_permissions])
class ModelsPermissionsChecksTests(SimpleTestCase):
    def test_clashing_default_permissions(self):
        """
        Test for clashing default permissions.
        
        This function checks for a clash between a custom permission and a built-in permission for a model named 'auth_tests.Checked'. It ensures that the codename 'change_checked' for the custom permission does not conflict with any built-in permissions.
        
        Parameters:
        None
        
        Returns:
        A list of Django `checks.Error` objects, where each error indicates a clash between a custom and a built-in permission. In this case, the error is expected to be a single `
        """

        class Checked(models.Model):
            class Meta:
                permissions = [
                    ('change_checked', 'Can edit permission (duplicate)')
                ]
        errors = checks.run_checks(self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Error(
                "The permission codenamed 'change_checked' clashes with a builtin "
                "permission for model 'auth_tests.Checked'.",
                obj=Checked,
                id='auth.E005',
            ),
        ])

    def test_non_clashing_custom_permissions(self):
        """
        Tests the non-clashing of custom permissions in a Django model.
        
        This function checks if custom permissions defined in a Django model's Meta class do not clash with any existing permissions. It creates a model with specified custom permissions and runs Django's model checks to ensure there are no conflicts.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If there are any errors detected during the check.
        
        Note:
        The function uses Django's internal checks mechanism to validate the model's permissions.
        """

        class Checked(models.Model):
            class Meta:
                permissions = [
                    ('my_custom_permission', 'Some permission'),
                    ('other_one', 'Some other permission'),
                ]
        errors = checks.run_checks(self.apps.get_app_configs())
        self.assertEqual(errors, [])

    def test_clashing_custom_permissions(self):
        class Checked(models.Model):
            class Meta:
                permissions = [
                    ('my_custom_permission', 'Some permission'),
                    ('other_one', 'Some other permission'),
                    ('my_custom_permission', 'Some permission with duplicate permission code'),
                ]
        errors = checks.run_checks(self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Error(
                "The permission codenamed 'my_custom_permission' is duplicated for "
                "model 'auth_tests.Checked'.",
                obj=Checked,
                id='auth.E006',
            ),
        ])

    def test_verbose_name_max_length(self):
        class Checked(models.Model):
            class Meta:
                verbose_name = 'some ridiculously long verbose name that is out of control' * 5
        errors = checks.run_checks(self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Error(
                "The verbose_name of model 'auth_tests.Checked' must be at most 244 "
                "characters for its builtin permission names to be at most 255 characters.",
                obj=Checked,
                id='auth.E007',
            ),
        ])

    def test_model_name_max_length(self):
        model_name = 'X' * 94
        model = type(model_name, (models.Model,), {'__module__': self.__module__})
        errors = checks.run_checks(self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Error(
                "The name of model 'auth_tests.%s' must be at most 93 "
                "characters for its builtin permission codenames to be at "
                "most 100 characters." % model_name,
                obj=model,
                id='auth.E011',
            ),
        ])

    def test_custom_permission_name_max_length(self):
        custom_permission_name = 'some ridiculously long verbose name that is out of control' * 5

        class Checked(models.Model):
            class Meta:
                permissions = [
                    ('my_custom_permission', custom_permission_name),
                ]
        errors = checks.run_checks(self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Error(
                "The permission named '%s' of model 'auth_tests.Checked' is longer "
                "than 255 characters." % custom_permission_name,
                obj=Checked,
                id='auth.E008',
            ),
        ])

    def test_custom_permission_codename_max_length(self):
        """
        Tests the maximum length of custom permission codenames.
        
        This function checks if a custom permission codename exceeds the maximum allowed length of 100 characters. It creates a model with a custom permission and then runs model checks to validate the codename length. If the codename is too long, it returns an error message indicating the model and the specific codename that exceeds the limit.
        
        Parameters:
        None
        
        Returns:
        list: A list of errors, where each error is an instance of `
        """

        custom_permission_codename = 'x' * 101

        class Checked(models.Model):
            class Meta:
                permissions = [
                    (custom_permission_codename, 'Custom permission'),
                ]

        errors = checks.run_checks(self.apps.get_app_configs())
        self.assertEqual(errors, [
            checks.Error(
                "The permission codenamed '%s' of model 'auth_tests.Checked' "
                "is longer than 100 characters." % custom_permission_codename,
                obj=Checked,
                id='auth.E012',
            ),
        ])

    def test_empty_default_permissions(self):
        class Checked(models.Model):
            class Meta:
                default_permissions = ()

        self.assertEqual(checks.run_checks(self.apps.get_app_configs()), [])
