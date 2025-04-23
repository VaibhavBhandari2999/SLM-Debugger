import sys
from unittest.mock import MagicMock


class MyCairoCffi(MagicMock):
    __name__ = "cairocffi"


def setup(app):
    """
    Setup function for modifying the CairoCffi module.
    
    This function is designed to be used with the Sphinx documentation system. It modifies the `sys.modules` dictionary to replace the original `cairocffi` module with a custom `MyCairoCffi` module. The function ensures that the modified module is safe for parallel processing.
    
    Parameters:
    app (Sphinx.application.Sphinx): The Sphinx application object.
    
    Returns:
    dict: A dictionary indicating that the modified module is safe for parallel processing.
    """

    sys.modules.update(
        cairocffi=MyCairoCffi(),
    )
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
