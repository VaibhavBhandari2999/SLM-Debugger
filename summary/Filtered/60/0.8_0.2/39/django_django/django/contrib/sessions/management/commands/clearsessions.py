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
        Clears expired sessions from the session store.
        
        This function imports the session engine specified in the settings and clears any expired sessions. If the session engine does not support clearing expired sessions, a warning message is printed to the stderr.
        
        Parameters:
        **options: Additional keyword arguments that are not used in this function.
        
        Returns:
        None
        
        Raises:
        ImportError: If the session engine cannot be imported.
        NotImplementedError: If the session engine does not support clearing expired sessions.
        """

        engine = import_module(settings.SESSION_ENGINE)
        try:
            engine.SessionStore.clear_expired()
        except NotImplementedError:
            self.stderr.write("Session engine '%s' doesn't support clearing "
                              "expired sessions.\n" % settings.SESSION_ENGINE)
