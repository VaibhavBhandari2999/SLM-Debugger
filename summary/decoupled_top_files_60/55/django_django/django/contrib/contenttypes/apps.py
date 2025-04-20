from django.apps import AppConfig
from django.contrib.contenttypes.checks import (
    check_generic_foreign_keys, check_model_name_lengths,
)
from django.core import checks
from django.db.models.signals import post_migrate, pre_migrate
from django.utils.translation import gettext_lazy as _

from .management import (
    create_contenttypes, inject_rename_contenttypes_operations,
)


class ContentTypesConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'django.contrib.contenttypes'
    verbose_name = _("Content Types")

    def ready(self):
        """
        Function to prepare the application for database operations.
        
        This function connects several signals and checks to the application, ensuring that it is ready for database migrations and model validations.
        
        Parameters:
        None
        
        Returns:
        None
        
        Signals connected:
        - pre_migrate: inject_rename_contenttypes_operations is connected as a receiver, which is triggered before the database migrations.
        - post_migrate: create_contenttypes is connected as a receiver, which is triggered after the database migrations.
        
        Checks registered:
        - check_generic
        """

        pre_migrate.connect(inject_rename_contenttypes_operations, sender=self)
        post_migrate.connect(create_contenttypes)
        checks.register(check_generic_foreign_keys, checks.Tags.models)
        checks.register(check_model_name_lengths, checks.Tags.models)
