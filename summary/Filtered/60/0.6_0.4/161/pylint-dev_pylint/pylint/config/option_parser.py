# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE

import optparse  # pylint: disable=deprecated-module

from pylint.config.option import Option


def _level_options(group, outputlevel):
    """
    Generate a list of options from a given group that are suitable for a specified output level.
    
    This function filters a list of options from a group based on their level attribute and the provided output level. It ensures that only options with a level less than or equal to the output level and that do not have their help suppressed are included in the result.
    
    Parameters:
    group (OptionGroup): The group of options to filter.
    outputlevel (int): The desired output level to filter the options by.
    """

    return [
        option
        for option in group.option_list
        if (getattr(option, "level", 0) or 0) <= outputlevel
        and option.help is not optparse.SUPPRESS_HELP
    ]


class OptionParser(optparse.OptionParser):
    def __init__(self, option_class, *args, **kwargs):
        super().__init__(option_class=Option, *args, **kwargs)

    def format_option_help(self, formatter=None):
        """
        Format and return the help for the options in the current formatter.
        
        This method generates a formatted help message for the options in the current formatter. It can accept an optional formatter object and uses the stored option strings to format the help. The method returns a string containing the formatted help.
        
        Parameters:
        formatter (optparse.OptionHelpFormatter, optional): The formatter object used to format the help. If not provided, the current formatter is used.
        
        Returns:
        str: A string containing the formatted help for
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

    def _match_long_opt(self, opt):
        """Disable abbreviations."""
        if opt not in self._long_opt:
            raise optparse.BadOptionError(opt)
        return opt
