import os

import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for a clustering package.
    
    This function configures the setup for a clustering package, including adding an extension module and a subpackage for tests. It also specifies the libraries to be linked during compilation.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to an empty string.
    - top_path (str, optional): The top-level path. Defaults to None.
    
    Returns:
    - config (Configuration): The configuration object for the clustering package, containing the extension and
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
