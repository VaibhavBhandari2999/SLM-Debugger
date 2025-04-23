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
        Function to add command-line arguments for displaying and comparing Django settings.
        
        This function configures the argument parser to accept various options for displaying and comparing Django settings. The function does not return any value but modifies the provided parser object.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser object to which the arguments will be added.
        
        Key Arguments:
        --all (bool): If set to True, displays all settings, regardless of their value. In "hash" mode, default values are prefixed by
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
        Generate a unified output of settings comparison.
        
        This function compares user settings with default settings and generates a unified output. The output includes differences, additions, and, optionally, all settings.
        
        Parameters:
        user_settings (dict): A dictionary containing user settings.
        default_settings (dict): A dictionary containing default settings.
        all (bool, optional): If True, includes all settings in the output. Defaults to False.
        
        Returns:
        list: A list of strings representing the unified output of settings comparison.
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
