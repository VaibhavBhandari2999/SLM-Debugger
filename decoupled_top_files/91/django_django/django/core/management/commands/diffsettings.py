"""
This Python script is designed to be used as a Django management command to display differences between the current Django settings and either Django's default settings or another custom settings module. It leverages the `django.conf` module to manage settings and provides detailed comparisons through two distinct output formats: "hash" and "unified".

#### Classes:
- **Command**: A subclass of `BaseCommand` that defines the behavior of the management command. It handles parsing command-line arguments and processing the settings comparison.

#### Functions:
- **add_arguments(parser)**: Adds command-line arguments to the argument parser, allowing users to specify which settings to display and the output format.
- **handle(**options)**: Executes the settings comparison logic, converting settings modules to dictionaries and applying
"""
from django.core.management.base import BaseCommand


def module_to_dict(module, omittable=lambda k: k.startswith('_') or not k.isupper()):
    """Convert a module namespace to a Python dictionary."""
    return {k: repr(getattr(module, k)) for k in dir(module) if not omittable(k)}


class Command(BaseCommand):
    help = """Displays differences between the current settings.py and Django's
    default settings."""

    requires_system_checks = []

    def add_arguments(self, parser):
        """
        Displays or compares Django settings.
        
        Args:
        parser (ArgumentParser): The argument parser instance to add arguments to.
        
        This function adds three command-line arguments to the provided `parser`:
        
        - `--all`: A boolean flag that, when set to `True`, displays all settings, regardless of their value. In "hash" mode, default values are prefixed by "###".
        - `--default`: A string argument representing the settings module to compare the current settings against. If
        """

        parser.add_argument(
            '--all', action='store_true',
            help=(
                'Display all settings, regardless of their value. In "hash" '
                'mode, default values are prefixed by "###".'
            ),
        )
        parser.add_argument(
            '--default', metavar='MODULE',
            help=(
                "The settings module to compare the current settings against. Leave empty to "
                "compare against Django's default settings."
            ),
        )
        parser.add_argument(
            '--output', default='hash', choices=('hash', 'unified'),
            help=(
                "Selects the output format. 'hash' mode displays each changed "
                "setting, with the settings that don't appear in the defaults "
                "followed by ###. 'unified' mode prefixes the default setting "
                "with a minus sign, followed by the changed setting prefixed "
                "with a plus sign."
            ),
        )

    def handle(self, **options):
        """
        Handle the settings comparison.
        
        This function compares the current Django settings with a set of default
        settings. It takes into account whether the settings are configured and
        processes them using the specified output format. The function uses the
        following key components:
        
        - `settings`: Manages the Django settings configuration.
        - `Settings`: A class that represents the default settings.
        - `global_settings`: Provides access to the global settings.
        - `module_to_dict`: Converts a module
        """

        from django.conf import Settings, global_settings, settings

        # Because settings are imported lazily, we need to explicitly load them.
        if not settings.configured:
            settings._setup()

        user_settings = module_to_dict(settings._wrapped)
        default = options['default']
        default_settings = module_to_dict(Settings(default) if default else global_settings)
        output_func = {
            'hash': self.output_hash,
            'unified': self.output_unified,
        }[options['output']]
        return '\n'.join(output_func(user_settings, default_settings, **options))

    def output_hash(self, user_settings, default_settings, **options):
        """
        Generates a list of configuration settings based on user and default settings.
        
        Args:
        user_settings (dict): A dictionary containing user-defined settings.
        default_settings (dict): A dictionary containing default settings.
        all (bool, optional): If True, includes all settings, even those that match the default values. Defaults to False.
        
        Returns:
        list: A list of strings representing configuration settings.
        """

        # Inspired by Postfix's "postconf -n".
        output = []
        for key in sorted(user_settings):
            if key not in default_settings:
                output.append("%s = %s  ###" % (key, user_settings[key]))
            elif user_settings[key] != default_settings[key]:
                output.append("%s = %s" % (key, user_settings[key]))
            elif options['all']:
                output.append("### %s = %s" % (key, user_settings[key]))
        return output

    def output_unified(self, user_settings, default_settings, **options):
        """
        Generates a unified output of settings by comparing user settings with default settings.
        
        Args:
        user_settings (dict): A dictionary containing user-defined settings.
        default_settings (dict): A dictionary containing default settings.
        all (bool, optional): If True, includes all settings in the output. Defaults to False.
        
        Returns:
        list: A list of strings representing the unified output of settings differences.
        """

        output = []
        for key in sorted(user_settings):
            if key not in default_settings:
                output.append(self.style.SUCCESS("+ %s = %s" % (key, user_settings[key])))
            elif user_settings[key] != default_settings[key]:
                output.append(self.style.ERROR("- %s = %s" % (key, default_settings[key])))
                output.append(self.style.SUCCESS("+ %s = %s" % (key, user_settings[key])))
            elif options['all']:
                output.append("  %s = %s" % (key, user_settings[key]))
        return output
