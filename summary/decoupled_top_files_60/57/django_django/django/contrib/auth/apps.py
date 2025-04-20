from django.apps import AppConfig
from django.core import checks
from django.db.models.query_utils import DeferredAttribute
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _

from . import get_user_model
from .checks import check_models_permissions, check_user_model
from .management import create_permissions
from .signals import user_logged_in


class AuthConfig(AppConfig):
    name = 'django.contrib.auth'
    verbose_name = _("Authentication and Authorization")

    def ready(self):
        """
        Function to initialize the authentication system.
        
        This function performs several key tasks:
        - Registers a signal handler for post_migrate to create permissions.
        - Checks if the `last_login` field exists in the user model and registers a signal handler to update it if necessary.
        - Registers model checks for the user model and permissions.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Actions:
        - Registers a signal handler for post_migrate to create permissions.
        - Checks if the `last_login` field exists in
        """

        post_migrate.connect(
            create_permissions,
            dispatch_uid="django.contrib.auth.management.create_permissions"
        )
        last_login_field = getattr(get_user_model(), 'last_login', None)
        # Register the handler only if UserModel.last_login is a field.
        if isinstance(last_login_field, DeferredAttribute):
            from .models import update_last_login
            user_logged_in.connect(update_last_login, dispatch_uid='update_last_login')
        checks.register(check_user_model, checks.Tags.models)
        checks.register(check_models_permissions, checks.Tags.models)
