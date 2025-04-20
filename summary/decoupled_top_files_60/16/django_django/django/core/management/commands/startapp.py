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
        
        This function is a custom handle method for creating a Django app. It takes in several keyword arguments:
        - `name`: The name of the Django app to be created.
        - `directory`: The target directory where the app will be created.
        
        Additional keyword arguments can be passed to customize the app creation process.
        
        This method ultimately calls the superclass's handle method with the specified arguments.
        
        Parameters:
        **options (dict): Additional keyword arguments to customize the app creation.
        
        Returns:
        """

        app_name = options.pop('name')
        target = options.pop('directory')
        super().handle('app', app_name, target, **options)
