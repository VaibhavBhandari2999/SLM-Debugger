import os

import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Function to configure the setup for a clustering package.
    
    This function is used to set up the configuration for a clustering package. It includes the addition of an extension module for fast computation of the expected mutual information and the inclusion of test subpackages.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path of the package. Defaults to None.
    
    Returns:
    - config (Configuration): The configuration
    """

    config = Configuration("cluster", parent_package, top_path)
    libraries = []
    if os.name == 'posix':
        libraries.append('m')
    config.add_extension("expected_mutual_info_fast",
                         sources=["expected_mutual_info_fast.pyx"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_subpackage("tests")

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration().todict())
