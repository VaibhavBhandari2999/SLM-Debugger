#!/usr/bin/env python
import sys

from django.conf import global_settings, settings
from django.core.management import execute_from_command_line


class Settings:
    def __getattr__(self, name):
        """
        Retrieve the value of a setting by its name.
        
        This method checks if the requested setting is 'FOO', returning 'bar' if true.
        Otherwise, it delegates to `global_settings` to retrieve the setting's value.
        
        Args:
        name (str): The name of the setting to retrieve.
        
        Returns:
        str: The value of the setting, either 'bar' or the value from `global_settings`.
        """

        if name == 'FOO':
            return 'bar'
        return getattr(global_settings, name)

    def __dir__(self):
        return super().__dir__() + dir(global_settings) + ['FOO']


if __name__ == '__main__':
    settings.configure(Settings())
    execute_from_command_line(sys.argv)
