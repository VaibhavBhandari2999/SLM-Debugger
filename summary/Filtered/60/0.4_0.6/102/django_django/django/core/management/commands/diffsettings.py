from django.core.management.base import BaseCommand


def module_to_dict(module, omittable=lambda k: k.startswith("_") or not k.isupper()):
    """Convert a module namespace to a Python dictionary."""
    return {k: repr(getattr(module, k)) for k in dir(module) if not omittable(k)}


class Command(BaseCommand):
    help = """Displays differences between the current settings.py and Django's
    default settings."""

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help=(
                'Display all settings, regardless of their value. In "hash" '
                'mode, default values are prefixed by "###".'
            ),
        )
        parser.add_argument(
            "--default",
            metavar="MODULE",
            help=(
                "The settings module to compare the current settings against. Leave "
                "empty to compare against Django's default settings."
            ),
        )
        parser.add_argument(
            "--output",
            default="hash",
            choices=("hash", "unified"),
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
        This function processes and compares settings from the Django project with a provided default settings module. It takes several keyword arguments to customize the output format and behavior.
        
        Parameters:
        **options (dict): Keyword arguments that include:
        - 'default' (bool): Whether to use the global settings or a default settings module.
        - 'output' (str): The output format, either 'hash' or 'unified'.
        - Other options specific to the chosen output format.
        
        Returns:
        str:
        """

        from django.conf import Settings, global_settings, settings

        # Because settings are imported lazily, we need to explicitly load them.
        if not settings.configured:
            settings._setup()

        user_settings = module_to_dict(settings._wrapped)
        default = options["default"]
        default_settings = module_to_dict(
            Settings(default) if default else global_settings
        )
        output_func = {
            "hash": self.output_hash,
            "unified": self.output_unified,
        }[options["output"]]
        return "\n".join(output_func(user_settings, default_settings, **options))

    def output_hash(self, user_settings, default_settings, **options):
        # Inspired by Postfix's "postconf -n".
        output = []
        for key in sorted(user_settings):
            if key not in default_settings:
                output.append("%s = %s  ###" % (key, user_settings[key]))
            elif user_settings[key] != default_settings[key]:
                output.append("%s = %s" % (key, user_settings[key]))
            elif options["all"]:
                output.append("### %s = %s" % (key, user_settings[key]))
        return output

    def output_unified(self, user_settings, default_settings, **options):
        """
        Generate a unified output of settings differences.
        
        This function compares user settings with default settings and outputs a unified view of the differences. It highlights settings that are unique to the user or differ from the defaults.
        
        Parameters:
        user_settings (dict): A dictionary containing the user's settings.
        default_settings (dict): A dictionary containing the default settings.
        all (bool, optional): If True, all settings will be listed, even if they match the default settings. Defaults to False.
        
        Returns:
        """

        output = []
        for key in sorted(user_settings):
            if key not in default_settings:
                output.append(
                    self.style.SUCCESS("+ %s = %s" % (key, user_settings[key]))
                )
            elif user_settings[key] != default_settings[key]:
                output.append(
                    self.style.ERROR("- %s = %s" % (key, default_settings[key]))
                )
                output.append(
                    self.style.SUCCESS("+ %s = %s" % (key, user_settings[key]))
                )
            elif options["all"]:
                output.append("  %s = %s" % (key, user_settings[key]))
        return output
