import os
from os.path import join

import numpy

from sklearn._build_utils import get_blas_info


def configuration(parent_package='', top_path=None):
    """
    Function to configure the setup for the 'linear_model' package.
    
    This function is used to set up the configuration for building and installing the 'linear_model' package. It includes extensions for different linear models and their optimization algorithms, and it handles the inclusion of necessary libraries and directories.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to ''.
    - top_path (str, optional): The top-level path. Defaults to None.
    
    Returns:
    - Configuration: A configuration object
    """

    from numpy.distutils.misc_util import Configuration

    config = Configuration('linear_model', parent_package, top_path)

    cblas_libs, blas_info = get_blas_info()

    if os.name == 'posix':
        cblas_libs.append('m')

    config.add_extension('cd_fast', sources=['cd_fast.pyx'],
                         libraries=cblas_libs,
                         include_dirs=[join('..', 'src', 'cblas'),
                                       numpy.get_include(),
                                       blas_info.pop('include_dirs', [])],
                         extra_compile_args=blas_info.pop('extra_compile_args',
                                                          []), **blas_info)

    config.add_extension('sgd_fast',
                         sources=['sgd_fast.pyx'],
                         include_dirs=[join('..', 'src', 'cblas'),
                                       numpy.get_include(),
                                       blas_info.pop('include_dirs', [])],
                         libraries=cblas_libs,
                         extra_compile_args=blas_info.pop('extra_compile_args',
                                                          []),
                         **blas_info)

    config.add_extension('sag_fast',
                         sources=['sag_fast.pyx'],
                         include_dirs=numpy.get_include())

    # add other directories
    config.add_subpackage('tests')

    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
