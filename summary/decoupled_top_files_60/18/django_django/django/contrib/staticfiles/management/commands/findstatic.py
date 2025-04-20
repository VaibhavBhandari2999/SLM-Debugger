import os

from django.contrib.staticfiles import finders
from django.core.management.base import LabelCommand


class Command(LabelCommand):
    help = "Finds the absolute paths for the given static file(s)."
    label = 'staticfile'

    def add_arguments(self, parser):
        """
        Adds command-line arguments to the parser.
        
        This method extends the functionality of the base class by adding a custom argument '--first'. This argument, when used, will only return the first match for each static file, effectively disabling the behavior of returning all matches. The argument is boolean in nature, where '--first' sets the 'all' flag to False.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which the custom argument will be added.
        
        Returns:
        None: This method does
        """

        super().add_arguments(parser)
        parser.add_argument(
            '--first', action='store_false', dest='all',
            help="Only return the first match for each static file.",
        )

    def handle_label(self, path, **options):
        """
        Handle a label to find a file.
        
        Parameters:
        path (str): The path of the file to be found.
        all (bool, optional): If True, return all matching files. Defaults to False.
        
        Returns:
        str: A message indicating the found file(s) or that no matching file was found. If verbosity is set to 2, it also includes the locations where the search was performed.
        """

        verbosity = options['verbosity']
        result = finders.find(path, all=options['all'])
        if verbosity >= 2:
            searched_locations = (
                "\nLooking in the following locations:\n  %s" %
                "\n  ".join(finders.searched_locations)
            )
        else:
            searched_locations = ''
        if result:
            if not isinstance(result, (list, tuple)):
                result = [result]
            result = (os.path.realpath(path) for path in result)
            if verbosity >= 1:
                file_list = '\n  '.join(result)
                return ("Found '%s' here:\n  %s%s" %
                        (path, file_list, searched_locations))
            else:
                return '\n'.join(result)
        else:
            message = ["No matching file found for '%s'." % path]
            if verbosity >= 2:
                message.append(searched_locations)
            if verbosity >= 1:
                self.stderr.write('\n'.join(message))
