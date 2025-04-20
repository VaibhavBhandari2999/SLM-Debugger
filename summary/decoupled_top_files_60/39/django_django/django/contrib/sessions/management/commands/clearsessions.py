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
        
        This function handles the clearing of expired sessions from the configured session engine. It attempts to call the `clear_expired` method on the session store. If the session engine does not support clearing expired sessions (indicated by a `NotImplementedError`), a message is written to the stderr indicating the unsupported session engine.
        
        Parameters:
        **options: Additional keyword arguments that may be required by the function, though they are not used in this specific implementation.
        
        Returns:
        """

        engine = import_module(settings.SESSION_ENGINE)
        try:
            engine.SessionStore.clear_expired()
        except NotImplementedError:
            self.stderr.write("Session engine '%s' doesn't support clearing "
                              "expired sessions.\n" % settings.SESSION_ENGINE)
