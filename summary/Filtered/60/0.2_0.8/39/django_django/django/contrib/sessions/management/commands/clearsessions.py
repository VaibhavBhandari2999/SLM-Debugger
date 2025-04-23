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
        Clear expired sessions from the session store.
        
        This function handles the clearing of expired sessions from the configured
        session engine. It attempts to clear expired sessions using the session
        engine specified in the settings. If the session engine does not support
        clearing expired sessions, a message is written to the standard error stream.
        
        Parameters:
        **options (dict): Additional keyword arguments that are not used in this function.
        
        Returns:
        None: This function does not return any value. It writes messages to the standard
        """

        engine = import_module(settings.SESSION_ENGINE)
        try:
            engine.SessionStore.clear_expired()
        except NotImplementedError:
            self.stderr.write("Session engine '%s' doesn't support clearing "
                              "expired sessions.\n" % settings.SESSION_ENGINE)
