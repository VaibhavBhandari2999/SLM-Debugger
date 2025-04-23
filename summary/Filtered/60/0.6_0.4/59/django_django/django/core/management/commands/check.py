from django.apps import apps
from django.core import checks
from django.core.checks.registry import registry
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Checks the entire Django project for potential problems."

    requires_system_checks = []

    def add_arguments(self, parser):
        """
        This function configures the argument parser for a command-line utility.
        
        The function takes a single argument:
        - `parser`: An instance of an argument parser (typically from the `argparse` module).
        
        The function adds several command-line arguments to the parser:
        - `args`: A list of app labels to run checks against. It is optional and can be specified multiple times.
        - `--tag` or `-t`: A list of tags to filter checks by. Multiple tags can be specified using the
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
