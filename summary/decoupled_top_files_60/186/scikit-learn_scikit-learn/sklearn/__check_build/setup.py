# Author: Virgile Fritsch <virgile.fritsch@inria.fr>
# License: BSD 3 clause

import numpy


def configuration(parent_package='', top_path=None):
    """
    Generate a configuration for building the `__check_build` extension.
    
    This function is used to configure the build process for the `__check_build` extension, which is typically used for testing purposes. It sets up the necessary details for compiling the extension module.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to an empty string.
    - top_path (str, optional): The top-level path. Defaults to None.
    
    Returns:
    - Configuration: An instance of the `Configuration
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
