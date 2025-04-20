# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE

import optparse  # pylint: disable=deprecated-module
import sys
import time


class _ManHelpFormatter(optparse.HelpFormatter):
    def __init__(
        self, indent_increment=0, max_help_position=24, width=79, short_first=0
    ):
        super().__init__(indent_increment, max_help_position, width, short_first)
        self.output_level: int

    def format_heading(self, heading):
        return f".SH {heading.upper()}\n"

    def format_description(self, description):
        return description

    def format_option(self, option):
        try:
            optstring = option.option_strings
        except AttributeError:
            optstring = self.format_option_strings(option)
        if option.help:
            help_text = self.expand_default(option)
            help_string = " ".join(line.strip() for line in help_text.splitlines())
            help_string = help_string.replace("\\", "\\\\")
            help_string = help_string.replace("[current:", "[default:")
        else:
            help_string = ""
        return f""".IP "{optstring}"
{help_string}
"""

    def format_head(self, optparser, pkginfo, section=1):
        """
        Formats the header section of a package information.
        
        This function generates a formatted header section for a package, including a title, short description, synopsis, and long description if available.
        
        Parameters:
        optparser (object): An object that provides program name and description.
        pkginfo (object): An object containing package information, including a description and long description.
        section (int, optional): The section number for the header. Defaults to 1.
        
        Returns:
        str: A formatted string representing the
        """

        long_desc = ""
        try:
            pgm = optparser._get_prog_name()
        except AttributeError:
            # py >= 2.4.X (dunno which X exactly, at least 2)
            pgm = optparser.get_prog_name()
        short_desc = self.format_short_description(pgm, pkginfo.description)
        if hasattr(pkginfo, "long_desc"):
            long_desc = self.format_long_description(pgm, pkginfo.long_desc)
        return f"""{self.format_title(pgm, section)}
{short_desc}
{self.format_synopsis(pgm)}
{long_desc}"""

    @staticmethod
    def format_title(pgm, section):
        date = (
            "%d-%02d-%02d"  # pylint: disable=consider-using-f-string
            % time.localtime()[:3]
        )
        return f'.TH {pgm} {section} "{date}" {pgm}'

    @staticmethod
    def format_short_description(pgm, short_desc):
        return f""".SH NAME
.B {pgm}
\\- {short_desc.strip()}
"""

    @staticmethod
    def format_synopsis(pgm):
        """
        Generates a formatted synopsis string for a program.
        
        This function creates a synopsis string that documents the usage of a program, including its name, options, and arguments. The synopsis is formatted in a specific style, suitable for inclusion in manual pages or documentation.
        
        Args:
        pgm (str): The name of the program for which the synopsis is being generated.
        
        Returns:
        str: A formatted synopsis string that can be used in documentation or manual pages.
        
        Example:
        >>> format_synopsis('my
        """

        return f""".SH SYNOPSIS
.B  {pgm}
[
.I OPTIONS
] [
.I <arguments>
]
"""

    @staticmethod
    def format_long_description(pgm, long_desc):
        long_desc = "\n".join(line.lstrip() for line in long_desc.splitlines())
        long_desc = long_desc.replace("\n.\n", "\n\n")
        if long_desc.lower().startswith(pgm):
            long_desc = long_desc[len(pgm) :]
        return f""".SH DESCRIPTION
.B {pgm}
{long_desc.strip()}
"""

    @staticmethod
    def format_tail(pkginfo):
        """
        Formats the tail section of a package documentation.
        
        This function generates the tail section of a package's documentation, which includes additional information such as references, bug reporting instructions, and author details.
        
        Args:
        pkginfo (object): An object containing package information such as `debian_name`, `mailinglist`, `author`, `author_email`, and `copyright`.
        
        Returns:
        str: The formatted tail section of the package documentation.
        """

        tail = f""".SH SEE ALSO
/usr/share/doc/pythonX.Y-{getattr(pkginfo, "debian_name", "pylint")}/

.SH BUGS
Please report bugs on the project\'s mailing list:
{pkginfo.mailinglist}

.SH AUTHOR
{pkginfo.author} <{pkginfo.author_email}>
"""
        if hasattr(pkginfo, "copyright"):
            tail += f"""
.SH COPYRIGHT
{pkginfo.copyright}
"""
        return tail

    def format_usage(self, usage):
        """Taken from optparse.IndentedHelpFormatter."""
        return f"Usage: {usage}\n"


def _generate_manpage(optparser, pkginfo, section=1, stream=sys.stdout, level=0):
    """
    Generate a manpage for a given option parser and package information.
    
    This function formats and outputs a manpage for a given option parser and package information. The manpage is written to the specified stream.
    
    Parameters:
    optparser (OptionParser): The option parser object to generate the manpage from.
    pkginfo (dict): A dictionary containing package information.
    section (int, optional): The section of the manpage. Defaults to 1.
    stream (TextIO, optional): The
    """

    formatter = _ManHelpFormatter()
    formatter.output_level = level
    formatter.parser = optparser
    print(formatter.format_head(optparser, pkginfo, section), file=stream)
    print(optparser.format_option_help(formatter), file=stream)
    print(formatter.format_tail(pkginfo), file=stream)
