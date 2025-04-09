"""
The provided Python file contains a Django management command named `Command`. This command is designed to perform comprehensive checks on a Django project, ensuring that various aspects of the application are configured correctly. The primary responsibility of this command is to run system checks, which can be targeted at specific applications or the entire project.

#### Main Components:
1. **Command Class**: 
   - **Purpose**: Defines a custom Django management command for running system checks.
   - **Methods**:
     - `add_arguments(parser)`: Adds command-line arguments to the parser, allowing users to specify which apps to check, tags to filter by, whether to list available tags, and other options.
     - `handle(*app_labels, **options)`: Executes the system checks
"""
from django.apps import apps
from django.core import checks
from django.core.checks.registry import registry
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Checks the entire Django project for potential problems."

    requires_system_checks = []

    def add_arguments(self, parser):
        """
        Add command-line arguments to the parser.
        
        Args:
        parser (argparse.ArgumentParser): The argument parser to which the
        arguments are added.
        
        This method adds several command-line arguments to the provided parser:
        
        - `args` (metavar='app_label', nargs='*'): Accepts zero or more app labels
        as positional arguments.
        - `--tag`, `-t` (action='append', dest='tags'): Allows specifying one or
        more tags to filter
        """

        parser.add_argument('args', metavar='app_label', nargs='*')
        parser.add_argument(
            '--tag', '-t', action='append', dest='tags',
            help='Run only checks labeled with given tag.',
        )
        parser.add_argument(
            '--list-tags', action='store_true',
            help='List available tags.',
        )
        parser.add_argument(
            '--deploy', action='store_true',
            help='Check deployment settings.',
        )
        parser.add_argument(
            '--fail-level',
            default='ERROR',
            choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
            help=(
                'Message level that will cause the command to exit with a '
                'non-zero status. Default is ERROR.'
            ),
        )
        parser.add_argument(
            '--database', action='append', dest='databases',
            help='Run database related checks against these aliases.',
        )

    def handle(self, *app_labels, **options):
        """
        Runs system checks.
        
        Args:
        *app_labels (str): Labels of Django apps to check.
        **options (dict): Options for the command, including 'deploy', 'list_tags', 'tags', 'fail_level', and 'databases'.
        
        Summary:
        This function runs system checks on specified Django apps or all installed apps. It can list available tags, validate tags, and execute checks based on the provided tags and fail level. The function handles deployment checks and displays the number
        """

        include_deployment_checks = options['deploy']
        if options['list_tags']:
            self.stdout.write('\n'.join(sorted(registry.tags_available(include_deployment_checks))))
            return

        if app_labels:
            app_configs = [apps.get_app_config(app_label) for app_label in app_labels]
        else:
            app_configs = None

        tags = options['tags']
        if tags:
            try:
                invalid_tag = next(
                    tag for tag in tags if not checks.tag_exists(tag, include_deployment_checks)
                )
            except StopIteration:
                # no invalid tags
                pass
            else:
                raise CommandError('There is no system check with the "%s" tag.' % invalid_tag)

        self.check(
            app_configs=app_configs,
            tags=tags,
            display_num_errors=True,
            include_deployment_checks=include_deployment_checks,
            fail_level=getattr(checks, options['fail_level']),
            databases=options['databases'],
        )
