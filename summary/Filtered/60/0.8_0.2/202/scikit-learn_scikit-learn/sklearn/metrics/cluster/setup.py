import os

import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for a Python package related to clustering algorithms.
    
    This function is typically used in the setup process of a Python package that includes clustering algorithms. It sets up the package configuration, including adding an extension module and a subpackage for tests.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path of the package. Defaults to None.
    
    Returns:
    - config (Configuration):
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
