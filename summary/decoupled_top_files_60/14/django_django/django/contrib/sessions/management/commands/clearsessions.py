from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Can be run as a cronjob or directly to clean out expired sessions "
        "(only with the database backend at the moment)."
    )

    def handle(self, **options):
        """
        Function to handle clearing expired sessions.
        
        This method is responsible for clearing expired sessions in the Django application. It imports the session engine specified in the settings and attempts to clear any expired sessions using the `SessionStore.clear_expired()` method. If the session engine does not support clearing expired sessions, a `NotImplementedError` is caught and an appropriate error message is displayed.
        
        Parameters:
        **options: Additional keyword arguments that may be required by the function.
        
        Returns:
        None: This function does not return
        """

        engine = import_module(settings.SESSION_ENGINE)
        try:
            engine.SessionStore.clear_expired()
        except NotImplementedError:
            self.stderr.write("Session engine '%s' doesn't support clearing "
                              "expired sessions.\n" % settings.SESSION_ENGINE)
