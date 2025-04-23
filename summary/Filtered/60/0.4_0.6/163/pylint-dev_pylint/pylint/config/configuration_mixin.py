# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/PyCQA/pylint/blob/main/CONTRIBUTORS.txt

import warnings

from pylint.config.option_manager_mixin import OptionsManagerMixIn
from pylint.config.options_provider_mixin import OptionsProviderMixIn


class ConfigurationMixIn(OptionsManagerMixIn, OptionsProviderMixIn):
    """Basic mixin for simple configurations which don't need the
    manager / providers model.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the ConfigurationMixIn class.
        
        This method initializes the ConfigurationMixIn class, handling deprecated functionality and setting up the necessary attributes. It also registers the class as an options provider.
        
        Parameters:
        *args: Variable length argument list. Typically used for positional arguments.
        **kwargs: Arbitrary keyword arguments. The 'usage' parameter is set to an empty string if not provided.
        
        Returns:
        None: This method does not return any value. It sets up the internal state of the class.
        
        Notes
        """

        # TODO: 3.0: Remove deprecated class
        warnings.warn(
            "ConfigurationMixIn has been deprecated and will be removed in pylint 3.0",
            DeprecationWarning,
        )
        if not args:
            kwargs.setdefault("usage", "")
        OptionsManagerMixIn.__init__(self, *args, **kwargs)
        OptionsProviderMixIn.__init__(self)
        if not getattr(self, "option_groups", None):
            self.option_groups = []
            for _, optdict in self.options:
                try:
                    gdef = (optdict["group"].upper(), "")
                except KeyError:
                    continue
                if gdef not in self.option_groups:
                    self.option_groups.append(gdef)
        self.register_options_provider(self, own_group=False)
