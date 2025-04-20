import os

from django.contrib.staticfiles import finders
from django.core.management.base import LabelCommand


class Command(LabelCommand):
    help = "Finds the absolute paths for the given static file(s)."
    label = 'staticfile'

    def add_arguments(self, parser):
        """
        Adds command-line arguments to the parser.
        
        This method extends the functionality of the base class by adding a custom argument '--first'. This argument, when used, will only return the first match for each static file, effectively stopping further searches once a match is found. The argument is boolean in nature, toggled via the 'store_false' action, and is stored under the 'all' attribute of the parser's namespace. If '--first' is not provided, the default behavior is to search for all
        """

        super().add_arguments(parser)
        parser.add_argument(
            '--first', action='store_false', dest='all',
            help="Only return the first match for each static file.",
        )

    def handle_label(self, path, **options):
        verbosity = options['verbosity']
        result = finders.find(path, all=options['all'])
        if verbosity >= 2:
            searched_locations = (
                "\nLooking in the following locations:\n  %s" %
                "\n  ".join([str(loc) for loc in finders.searched_locations])
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
