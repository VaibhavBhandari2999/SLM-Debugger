#!/usr/bin/env python
import sys

from django.conf import global_settings, settings
from django.core.management import execute_from_command_line


class Settings:
    def __getattr__(self, name):
        """
        Method: __getattr__
        Summary: This method is a custom attribute access handler for a class. It is called when an attribute lookup has not found the attribute in the usual places.
        Parameters:
        - name (str): The name of the attribute being accessed.
        Returns:
        - str: If the attribute name is 'FOO', it returns 'bar'. Otherwise, it returns the value of the attribute from the global_settings object.
        Notes:
        -
        """

        if name == 'FOO':
            return 'bar'
        return getattr(global_settings, name)

    def __dir__(self):
        return super().__dir__() + dir(global_settings) + ['FOO']


if __name__ == '__main__':
    settings.configure(Settings())
    execute_from_command_line(sys.argv)
