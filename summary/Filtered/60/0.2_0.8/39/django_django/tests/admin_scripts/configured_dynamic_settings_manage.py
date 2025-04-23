#!/usr/bin/env python
import sys

from django.conf import global_settings, settings
from django.core.management import execute_from_command_line


class Settings:
    def __getattr__(self, name):
        """
        This method is a custom attribute access handler for a class. It is called when an attribute that does not exist is accessed. If the attribute name is 'FOO', it returns the string 'bar'. Otherwise, it delegates the attribute lookup to the global_settings object using the `getattr` function.
        
        Parameters:
        - name (str): The name of the attribute that was accessed.
        
        Returns:
        - str: The value of the attribute if found, or 'bar' if the attribute name is 'FO
        """

        if name == 'FOO':
            return 'bar'
        return getattr(global_settings, name)

    def __dir__(self):
        return super().__dir__() + dir(global_settings) + ['FOO']


if __name__ == '__main__':
    settings.configure(Settings())
    execute_from_command_line(sys.argv)
