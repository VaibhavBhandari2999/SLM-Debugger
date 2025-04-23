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
        
        This function creates a new Django app with the specified name in the given directory.
        
        Parameters:
        app_name (str): The name of the Django app to be created.
        directory (str): The directory where the app will be created.
        
        Keyword Arguments:
        Additional keyword arguments that will be passed to the parent class's handle method.
        
        Returns:
        None: This function does not return any value. It is expected to create a new Django app in the specified directory.
        """

        app_name = options.pop('name')
        target = options.pop('directory')
        super().handle('app', app_name, target, **options)
