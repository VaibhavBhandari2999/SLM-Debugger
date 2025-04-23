from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.management.commands.runserver import (
    Command as RunserverCommand,
)


class Command(RunserverCommand):
    help = "Starts a lightweight web server for development and also serves static files."

    def add_arguments(self, parser):
        """
        This function adds command-line arguments to the argument parser for a Django application.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which the arguments will be added.
        
        Key Arguments:
        --nostatic (bool): If provided, tells Django not to automatically serve static files at STATIC_URL. Default is to serve static files.
        --insecure (bool): If provided, allows serving static files even if DEBUG is set to False. By default, serving static files is only allowed when DEBUG
        """

        super().add_arguments(parser)
        parser.add_argument(
            '--nostatic', action="store_false", dest='use_static_handler',
            help='Tells Django to NOT automatically serve static files at STATIC_URL.',
        )
        parser.add_argument(
            '--insecure', action="store_true", dest='insecure_serving',
            help='Allows serving static files even if DEBUG is False.',
        )

    def get_handler(self, *args, **options):
        """
        Return the static files serving handler wrapping the default handler,
        if static files should be served. Otherwise return the default handler.
        """
        handler = super().get_handler(*args, **options)
        use_static_handler = options['use_static_handler']
        insecure_serving = options['insecure_serving']
        if use_static_handler and (settings.DEBUG or insecure_serving):
            return StaticFilesHandler(handler)
        return handler
