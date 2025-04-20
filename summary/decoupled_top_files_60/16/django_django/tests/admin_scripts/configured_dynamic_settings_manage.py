#!/usr/bin/env python
import sys

from django.conf import global_settings, settings
from django.core.management import execute_from_command_line


class Settings:
    def __getattr__(self, name):
        """
        This method is used to dynamically retrieve attributes from the object. If the attribute name is 'FOO', it returns 'bar'. For any other attribute, it attempts to retrieve the attribute from the global_settings object. The method does not accept any parameters and returns the value of the requested attribute.
        
        Key Parameters:
        - name: The name of the attribute to be retrieved (string).
        
        Return Value:
        - The value of the requested attribute (string or any other type of value depending on the attribute). If
        """

        if name == 'FOO':
            return 'bar'
        return getattr(global_settings, name)

    def __dir__(self):
        return super().__dir__() + dir(global_settings) + ['FOO']


if __name__ == '__main__':
    settings.configure(Settings())
    execute_from_command_line(sys.argv)
