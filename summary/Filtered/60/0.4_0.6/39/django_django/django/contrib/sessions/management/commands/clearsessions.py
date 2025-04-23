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
        Function to handle clearing of expired sessions.
        
        This function is designed to clear expired sessions from the session engine specified in the settings. It uses the session engine to clear any expired sessions.
        
        Parameters:
        **options: Additional keyword arguments that may be required by the session engine.
        
        Returns:
        None: This function does not return any value. It performs the clearing of expired sessions.
        
        Raises:
        NotImplementedError: If the session engine does not support clearing expired sessions, this exception is raised and an error message is
        """

        engine = import_module(settings.SESSION_ENGINE)
        try:
            engine.SessionStore.clear_expired()
        except NotImplementedError:
            self.stderr.write("Session engine '%s' doesn't support clearing "
                              "expired sessions.\n" % settings.SESSION_ENGINE)
