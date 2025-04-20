import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections


class Command(BaseCommand):
    help = (
        "Runs the command-line client for specified database, or the "
        "default database if none is provided."
    )

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help=(
                "Nominates a database onto which to open a shell. Defaults to the "
                '"default" database.'
            ),
        )
        parameters = parser.add_argument_group("parameters", prefix_chars="--")
        parameters.add_argument("parameters", nargs="*")

    def handle(self, **options):
        """
        Handle a database command execution.
        
        This function executes a shell command on the specified database connection. It takes the following parameters:
        - `**options`: A dictionary containing the following keys:
        - `database`: The name of the database to connect to.
        - `parameters`: A list of parameters to pass to the shell command.
        
        The function attempts to run the shell command using the specified database connection. If the command is not found, it raises a `CommandError` with a message indicating the missing
        """

        connection = connections[options["database"]]
        try:
            connection.client.runshell(options["parameters"])
        except FileNotFoundError:
            # Note that we're assuming the FileNotFoundError relates to the
            # command missing. It could be raised for some other reason, in
            # which case this error message would be inaccurate. Still, this
            # message catches the common case.
            raise CommandError(
                "You appear not to have the %r program installed or on your path."
                % connection.client.executable_name
            )
        except subprocess.CalledProcessError as e:
            raise CommandError(
                '"%s" returned non-zero exit status %s.'
                % (
                    " ".join(e.cmd),
                    e.returncode,
                ),
                returncode=e.returncode,
            )
