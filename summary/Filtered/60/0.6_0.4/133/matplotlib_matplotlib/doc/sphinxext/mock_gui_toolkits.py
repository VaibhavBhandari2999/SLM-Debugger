import sys
from unittest.mock import MagicMock


class MyCairoCffi(MagicMock):
    __name__ = "cairocffi"


def setup(app):
    """
    Setup function for modifying the cairocffi module during Sphinx documentation build.
    
    This function is designed to be used with the Sphinx documentation builder. It dynamically updates the `sys.modules` with a custom `MyCairoCffi` object, effectively replacing the original `cairocffi` module during the build process.
    
    Parameters:
    app (sphinx.application.Sphinx): The Sphinx application object.
    
    Returns:
    dict: A dictionary indicating that the setup is safe for parallel processing. The keys 'parallel_read
    """

    sys.modules.update(
        cairocffi=MyCairoCffi(),
    )
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
