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
    name = 'django.contrib.contenttypes'
    verbose_name = _("Content Types")

    def ready(self):
        """
        Function to prepare the application for migration.
        
        This function connects several signals and checks to the application. It ensures that the necessary operations are performed during the pre-migration and post-migration phases, and it registers specific checks for model validation.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Signals Connected:
        - pre_migrate: inject_rename_contenttypes_operations
        - post_migrate: create_contenttypes
        
        Checks Registered:
        - check_generic_foreign_keys:
        """

        pre_migrate.connect(inject_rename_contenttypes_operations, sender=self)
        post_migrate.connect(create_contenttypes)
        checks.register(check_generic_foreign_keys, checks.Tags.models)
        checks.register(check_model_name_lengths, checks.Tags.models)
