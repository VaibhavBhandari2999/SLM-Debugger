# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE

import optparse  # pylint: disable=deprecated-module
import sys
import time


class _ManHelpFormatter(optparse.HelpFormatter):
    def __init__(
        """
        Initialize a new instance of the class with specified indentation increment, maximum help position, width, and short first flag.
        
        Args:
        indent_increment (int): The amount to increment the indentation level.
        max_help_position (int): The maximum position for help text.
        width (int): The width of the output.
        short_first (bool): Whether to display short options before long ones.
        
        Attributes:
        output_level (int): The current output level.
        """

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
    Generate a man page from an OptionParser object.
    
    Args:
    optparser (OptionParser): The OptionParser object to generate the man page from.
    pkginfo (dict): Information about the package.
    section (int, optional): The section of the man page. Defaults to 1.
    stream (TextIO, optional): The stream to write the man page to. Defaults to sys.stdout.
    level (int, optional): The output level. Defaults to 0.
    """

    formatter = _ManHelpFormatter()
    formatter.output_level = level
    formatter.parser = optparser
    print(formatter.format_head(optparser, pkginfo, section), file=stream)
    print(optparser.format_option_help(formatter), file=stream)
    print(formatter.format_tail(pkginfo), file=stream)
