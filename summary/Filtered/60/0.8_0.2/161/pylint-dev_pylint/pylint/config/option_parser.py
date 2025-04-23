# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE

import optparse  # pylint: disable=deprecated-module

from pylint.config.option import Option


def _level_options(group, outputlevel):
    """
    Extracts options from a given group that are suitable for the specified output level.
    
    This function filters a list of options from a command-line group based on their level and help status. It returns a list of options that are appropriate for the given output level.
    
    Parameters:
    group (OptionGroup): The command-line option group from which to extract options.
    outputlevel (int): The desired output level to filter the options by.
    
    Returns:
    list: A list of options that are suitable for the
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
        raise optparse.BadOptionError(opt)
        return opt
