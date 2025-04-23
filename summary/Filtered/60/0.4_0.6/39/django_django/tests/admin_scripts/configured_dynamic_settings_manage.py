#!/usr/bin/env python
import sys

from django.conf import global_settings, settings
from django.core.management import execute_from_command_line


class Settings:
    def __getattr__(self, name):
        """
        Retrieve a setting from the global settings object. If the setting 'FOO' is requested, return 'bar' instead. If the setting does not exist, raise an AttributeError.
        
        Parameters:
        name (str): The name of the setting to retrieve.
        
        Returns:
        str: The value of the setting.
        
        Raises:
        AttributeError: If the setting does not exist in the global settings and is not 'FOO'.
        """

        if name == 'FOO':
            return 'bar'
        return getattr(global_settings, name)

    def __dir__(self):
        return super().__dir__() + dir(global_settings) + ['FOO']


if __name__ == '__main__':
    settings.configure(Settings())
    execute_from_command_line(sys.argv)
