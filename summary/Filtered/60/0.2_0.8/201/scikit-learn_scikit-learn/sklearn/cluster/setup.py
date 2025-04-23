# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
# License: BSD 3 clause
import os

import numpy


def configuration(parent_package='', top_path=None):
    """
    Function to configure the setup of the 'cluster' package.
    
    This function is used to set up the configuration for building and installing the 'cluster' package. It includes the necessary details for compiling and linking C++ extensions and adding tests.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path. Defaults to None.
    
    Returns:
    - Configuration: An instance of the Configuration class from numpy
    """

    from numpy.distutils.misc_util import Configuration

    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    config = Configuration('cluster', parent_package, top_path)
    config.add_extension('_dbscan_inner',
                         sources=['_dbscan_inner.pyx'],
                         include_dirs=[numpy.get_include()],
                         language="c++")

    config.add_extension('_hierarchical_fast',
                         sources=['_hierarchical_fast.pyx'],
                         language="c++",
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_extension('_k_means_elkan',
                         sources=['_k_means_elkan.pyx'],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_extension('_k_means_fast',
                         sources=['_k_means_fast.pyx'],
                         include_dirs=numpy.get_include(),
                         libraries=libraries)

    config.add_subpackage('tests')

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
