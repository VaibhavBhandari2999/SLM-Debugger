# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/PyCQA/pylint/blob/main/CONTRIBUTORS.txt

import optparse  # pylint: disable=deprecated-module
import warnings

from pylint.config.option import Option


def _level_options(group, outputlevel):
    """
    Generate a list of options from a group that are appropriate for the given output level.
    
    This function filters a list of options from a given group based on the specified output level. It returns a list of options where the level of each option is less than or equal to the specified output level, and the help text is not suppressed.
    
    Parameters:
    group (optparse.OptionGroup): The group containing the options to be filtered.
    outputlevel (int): The desired output level used to filter the options
    """

    return [
        option
        for option in group.option_list
        if (getattr(option, "level", 0) or 0) <= outputlevel
        and option.help is not optparse.SUPPRESS_HELP
    ]


class OptionParser(optparse.OptionParser):
    def __init__(self, option_class, *args, **kwargs):
        """
        Initialize the OptionParser with the given option class and other arguments.
        
        This method initializes the OptionParser with the specified option class and any additional positional and keyword arguments. It also issues a deprecation warning, as the OptionParser class is deprecated and will be removed in pylint 3.0.
        
        Parameters:
        option_class (class): The class to use for options.
        *args: Additional positional arguments to pass to the superclass initializer.
        **kwargs: Additional keyword arguments to pass to the superclass initializer
        """

        # TODO: 3.0: Remove deprecated class
        warnings.warn(
            "OptionParser has been deprecated and will be removed in pylint 3.0",
            DeprecationWarning,
        )
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

    def _match_long_opt(self, opt):  # pragma: no cover # Unused
        """Disable abbreviations."""
        if opt not in self._long_opt:
            raise optparse.BadOptionError(opt)
        return opt
