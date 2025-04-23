from django.core.management.base import BaseCommand
from django.core.management.sql import sql_flush
from django.db import DEFAULT_DB_ALIAS, connections


class Command(BaseCommand):
    help = (
        "Returns a list of the SQL statements required to return all tables in "
        "the database to the state they were in just after they were installed."
    )

    output_transaction = True

    def add_arguments(self, parser):
        """
        Adds custom arguments to the argument parser.
        
        This method extends the functionality of the base class by adding a custom argument '--database'. This argument allows specifying a database alias for which the SQL will be printed. If no alias is provided, it defaults to the 'default' database.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which the custom argument will be added.
        
        Returns:
        None: This method does not return any value. It modifies the provided argument parser in place.
        """

        super().add_arguments(parser)
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help='Nominates a database to print the SQL for. Defaults to the "default" database.',
        )

    def handle(self, **options):
        """
        Function to handle database flushing.
        
        This function processes SQL statements for flushing a database. It takes a style object and a connection dictionary as input and returns a string of SQL statements.
        
        Parameters:
        self: The instance of the class containing this method.
        **options: A dictionary of command-line options. It includes 'database' to specify the database to flush and 'verbosity' to control the amount of output.
        
        Returns:
        str: A string containing the SQL statements for flushing the database, or an
        """

        sql_statements = sql_flush(self.style, connections[options['database']])
        if not sql_statements and options['verbosity'] >= 1:
            self.stderr.write('No tables found.')
        return '\n'.join(sql_statements)
