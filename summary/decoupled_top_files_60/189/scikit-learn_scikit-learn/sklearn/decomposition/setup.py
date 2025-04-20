import os
import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Function to configure the setup for the 'decomposition' package.
    
    This function sets up the configuration for building and installing the 'decomposition' package. It includes the necessary extensions and subpackages.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to an empty string.
    - top_path (str, optional): The top-level path. Defaults to None.
    
    Returns:
    - config (Configuration): The configuration object for the 'decomposition' package, including extensions and subpackages
    """

    config = Configuration("decomposition", parent_package, top_path)

    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    config.add_extension("_online_lda",
                         sources=["_online_lda.pyx"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_extension('cdnmf_fast',
                         sources=['cdnmf_fast.pyx'],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_subpackage("tests")

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration().todict())
