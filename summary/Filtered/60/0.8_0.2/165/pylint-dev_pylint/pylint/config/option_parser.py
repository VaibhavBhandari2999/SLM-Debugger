# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/PyCQA/pylint/blob/main/CONTRIBUTORS.txt

import optparse  # pylint: disable=deprecated-module
import warnings

from pylint.config.option import Option


def _level_options(group, outputlevel):
    """
    Generate a list of options from a group that are suitable for a given output level.
    
    This function filters a list of options from a given group based on their level and help status. It returns a list of options that have a level less than or equal to the specified output level and have a help message that is not suppressed.
    
    Parameters:
    group (optparse.OptionGroup): The group containing the options to be filtered.
    outputlevel (int): The maximum level of options to include in the output
    """

    return [
        option
        for option in group.option_list
        if (getattr(option, "level", 0) or 0) <= outputlevel
        and option.help is not optparse.SUPPRESS_HELP
    ]


class OptionParser(optparse.OptionParser):
    def __init__(self, option_class, *args, **kwargs):
        # TODO: 3.0: Remove deprecated class
        warnings.warn(
            "OptionParser has been deprecated and will be removed in pylint 3.0",
            DeprecationWarning,
        )
        super().__init__(option_class=Option, *args, **kwargs)

    def format_option_help(self, formatter=None):
        """
        Format and return the help for the options in the current object.
        
        This method generates a formatted help string for the options available in the object. It can optionally accept a formatter object to customize the output format.
        
        Parameters:
        formatter (optparse.OptionHelpFormatter, optional): A formatter object used to format the help text. If not provided, the object's internal formatter will be used.
        
        Returns:
        str: A formatted string containing the help information for the options.
        """

        if formatter is None:
            formatter = self.formatter
        outputlevel = getattr(formatter, "output_level", 0)
        formatter.store_option_strings(self)
        result = [formatter.format_heading("Options")]
        formatter.indent()
        if self.option_list:
            result.append(optparse.OptionContainer.format_option_help(self, formatter))
            result.append("\n")
        for group in self.option_groups:
            if group.level <= outputlevel and (
                group.description or _level_options(group, outputlevel)
            ):
                result.append(group.format_help(formatter))
                result.append("\n")
        formatter.dedent()
        # Drop the last "\n", or the header if no options or option groups:
        return "".join(result[:-1])

    def _match_long_opt(self, opt):  # pragma: no cover # Unused
        """Disable abbreviations."""
        if opt not in self._long_opt:
            raise optparse.BadOptionError(opt)
        return opt
ise optparse.BadOptionError(opt)
        return opt
