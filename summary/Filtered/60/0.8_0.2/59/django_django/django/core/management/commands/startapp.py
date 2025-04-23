from django.core.management.templates import TemplateCommand


class Command(TemplateCommand):
    help = (
        "Creates a Django app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide an application name."

    def handle(self, **options):
        """
        Generates a Django app.
        
        This function is designed to create a new Django application within a specified directory. It accepts several parameters:
        
        Parameters:
        - name (str): The name of the Django app to be created.
        - directory (str): The target directory where the app will be created.
        - **options: Additional keyword arguments that can be passed to customize the app creation process.
        
        Returns:
        None: This function does not return any value. It performs the app creation in place.
        """

        app_name = options.pop('name')
        target = options.pop('directory')
        super().handle('app', app_name, target, **options)
