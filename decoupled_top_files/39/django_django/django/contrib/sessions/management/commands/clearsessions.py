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
        
        This function imports the specified session engine, then attempts to clear
        any expired sessions using the `clear_expired` method of the session store.
        If the session engine does not support clearing expired sessions, a message
        is written to the stderr indicating that the engine does not support this
        functionality.
        
        Args:
        **options: Additional keyword arguments (not used in this function).
        
        Returns:
        None
        
        Raises:
        ImportError
        """

        engine = import_module(settings.SESSION_ENGINE)
        try:
            engine.SessionStore.clear_expired()
        except NotImplementedError:
            self.stderr.write("Session engine '%s' doesn't support clearing "
                              "expired sessions.\n" % settings.SESSION_ENGINE)
