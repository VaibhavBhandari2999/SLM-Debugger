from django.core.management.templates import TemplateCommand


class Command(TemplateCommand):
    help = (
        "Creates a Django app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide an application name."

    def handle(self, **options):
        """
        Generates a Django app within a specified directory.
        
        This function is designed to create a new Django app with the given name in the specified directory. It accepts several keyword arguments to customize the app's creation process.
        
        Parameters:
        app_name (str): The name of the Django app to be created.
        directory (str): The directory where the app will be created.
        **options: Additional keyword arguments that can be used to customize the app's creation process. These options are passed directly to Django
        """

        app_name = options.pop('name')
        target = options.pop('directory')
        super().handle('app', app_name, target, **options)
