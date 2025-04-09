from django.core.management.base import BaseCommand


def module_to_dict(module, omittable=lambda k: k.startswith('_') or not k.isupper()):
    """Convert a module namespace to a Python dictionary."""
    return {k: repr(getattr(module, k)) for k in dir(module) if not omittable(k)}


class Command(BaseCommand):
    help = """Displays differences between the current settings.py and Django's
    default settings."""

    requires_system_checks = False

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
        Generates a unified or hashed comparison of Django settings.
        
        Args:
        **options: Keyword arguments that include:
        - 'output': Specifies the output format ('hash' or 'unified').
        - 'default': A boolean indicating whether to use the default settings.
        
        Returns:
        A string representing the comparison result, either in a unified or hashed format.
        """

        from django.conf import settings, Settings, global_settings

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
