import os

import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for a machine learning cluster module.
    
    This function configures the setup for a machine learning cluster module. It sets up the necessary extensions and subpackages for the module. The function can be customized with a parent package name and the top path.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top path for the package. Defaults to None.
    
    Returns:
    - config (Configuration
    """

    config = Configuration("cluster", parent_package, top_path)
    libraries = []
    if os.name == 'posix':
        libraries.append('m')
    config.add_extension("_expected_mutual_info_fast",
                         sources=["_expected_mutual_info_fast.pyx"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_subpackage("tests")

    return config


if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration().todict())
