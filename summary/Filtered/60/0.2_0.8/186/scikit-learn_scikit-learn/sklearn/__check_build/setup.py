# Author: Virgile Fritsch <virgile.fritsch@inria.fr>
# License: BSD 3 clause

import numpy


def configuration(parent_package='', top_path=None):
    """
    Generate a configuration for building the __check_build module.
    
    This function is used to configure the build process for the __check_build module, which is typically used for testing the build environment. It sets up the necessary extension and includes the required directories.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to an empty string.
    - top_path (str, optional): The top path. Defaults to None.
    
    Returns:
    - config (Configuration): A Configuration object that contains the setup
    """

    from numpy.distutils.misc_util import Configuration
    config = Configuration('__check_build', parent_package, top_path)
    config.add_extension('_check_build',
                         sources=['_check_build.pyx'],
                         include_dirs=[numpy.get_include()])

    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
