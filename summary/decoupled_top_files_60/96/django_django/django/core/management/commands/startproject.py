from django.core.checks.security.base import SECRET_KEY_INSECURE_PREFIX
from django.core.management.templates import TemplateCommand

from ..utils import get_random_secret_key


class Command(TemplateCommand):
    help = (
        "Creates a Django project directory structure for the given project "
        "name in the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide a project name."

    def handle(self, **options):
        """
        Generates a Django project with specified name and directory.
        
        This function creates a new Django project with the given project name and saves it in the specified directory. It also generates a random SECRET_KEY and includes it in the project's settings.
        
        Parameters:
        name (str): The name of the Django project.
        directory (str): The directory where the project will be created.
        
        Keyword Arguments:
        options (dict): Additional options to be passed to the Django project creation command.
        
        Returns:
        None:
        """

        project_name = options.pop("name")
        target = options.pop("directory")

        # Create a random SECRET_KEY to put it in the main settings.
        options["secret_key"] = SECRET_KEY_INSECURE_PREFIX + get_random_secret_key()

        super().handle("project", project_name, target, **options)
