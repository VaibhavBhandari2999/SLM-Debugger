import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS

UserModel = get_user_model()


class Command(BaseCommand):
    help = "Change a user's password for django.contrib.auth."
    requires_migrations_checks = True
    requires_system_checks = []

    def _get_pass(self, prompt="Password: "):
        """
        Retrieve a password from the user securely.
        
        This method prompts the user for a password using the specified prompt. The password is read securely to avoid displaying it on the screen. If the user does not provide a password (i.e., presses Enter without typing anything), a CommandError is raised indicating that the operation was aborted.
        
        Parameters:
        prompt (str): The prompt message to display to the user when asking for the password. Default is "Password: ".
        
        Returns:
        str: The password entered
        """

        p = getpass.getpass(prompt=prompt)
        if not p:
            raise CommandError("aborted")
        return p

    def add_arguments(self, parser):
        """
        Function to add command-line arguments for changing a user's password.
        
        This function is typically used in a Django management command to allow users to specify a username and a database to change the password for a specific user. If no username is provided, the current username is used by default. The function also allows specifying a different database to use for the operation.
        
        Args:
        parser (argparse.ArgumentParser): The argument parser to which the arguments will be added.
        
        Key Arguments:
        - `username` (optional
        """

        parser.add_argument(
            'username', nargs='?',
            help='Username to change password for; by default, it\'s the current username.',
        )
        parser.add_argument(
            '--database',
            default=DEFAULT_DB_ALIAS,
            help='Specifies the database to use. Default is "default".',
        )

    def handle(self, *args, **options):
        if options['username']:
            username = options['username']
        else:
            username = getpass.getuser()

        try:
            u = UserModel._default_manager.using(options['database']).get(**{
                UserModel.USERNAME_FIELD: username
            })
        except UserModel.DoesNotExist:
            raise CommandError("user '%s' does not exist" % username)

        self.stdout.write("Changing password for user '%s'" % u)

        MAX_TRIES = 3
        count = 0
        p1, p2 = 1, 2  # To make them initially mismatch.
        password_validated = False
        while (p1 != p2 or not password_validated) and count < MAX_TRIES:
            p1 = self._get_pass()
            p2 = self._get_pass("Password (again): ")
            if p1 != p2:
                self.stdout.write('Passwords do not match. Please try again.')
                count += 1
                # Don't validate passwords that don't match.
                continue
            try:
                validate_password(p2, u)
            except ValidationError as err:
                self.stderr.write('\n'.join(err.messages))
                count += 1
            else:
                password_validated = True

        if count == MAX_TRIES:
            raise CommandError("Aborting password change for user '%s' after %s attempts" % (u, count))

        u.set_password(p1)
        u.save()

        return "Password changed successfully for user '%s'" % u
