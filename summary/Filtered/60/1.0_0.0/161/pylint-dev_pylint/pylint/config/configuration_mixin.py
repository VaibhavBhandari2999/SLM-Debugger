# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE

from pylint.config.option_manager_mixin import OptionsManagerMixIn
from pylint.config.options_provider_mixin import OptionsProviderMixIn


class ConfigurationMixIn(OptionsManagerMixIn, OptionsProviderMixIn):
    """Basic mixin for simple configurations which don't need the
    manager / providers model
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the OptionsManagerMixIn and OptionsProviderMixIn classes.
        
        This method initializes the OptionsManagerMixIn and OptionsProviderMixIn classes. It sets the 'usage' parameter if it is not provided and registers the current object as an options provider.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments. The 'usage' key is used to set the usage string if not provided.
        
        Returns:
        None: This method does not return any value. It sets
        """

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
