# Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
# License: BSD 3 clause
import os

import numpy


def configuration(parent_package='', top_path=None):
    """
    Generates a configuration for a Python package.
    
    This function is used to configure the setup process for a Python package, particularly for extensions that need to be compiled. It sets up the necessary details for building C/C++ extensions using `numpy.distutils`.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path for the package. Defaults to None.
    
    Returns:
    - Configuration: An instance
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

    config.add_extension('_hierarchical',
                         sources=['_hierarchical.pyx'],
                         language="c++",
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_extension('_k_means_elkan',
                         sources=['_k_means_elkan.pyx'],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_extension('_k_means',
                         sources=['_k_means.pyx'],
                         include_dirs=numpy.get_include(),
                         libraries=libraries)

    config.add_subpackage('tests')

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
