import sys
from unittest.mock import MagicMock


class MyCairoCffi(MagicMock):
    __name__ = "cairocffi"


def setup(app):
    """
    Setup function for modifying the sys.modules with a custom CairoCffi object.
    
    This function is designed to be used as a setup function for an application. It updates the sys.modules dictionary with a custom instance of MyCairoCffi. The function ensures that the modifications are safe for parallel processing.
    
    Parameters:
    app: The application object that this setup function is associated with.
    
    Returns:
    A dictionary with two keys, 'parallel_read_safe' and 'parallel_write_safe', both set to True,
    """

    sys.modules.update(
        cairocffi=MyCairoCffi(),
    )
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
