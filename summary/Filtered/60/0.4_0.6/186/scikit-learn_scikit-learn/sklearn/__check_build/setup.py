# Author: Virgile Fritsch <virgile.fritsch@inria.fr>
# License: BSD 3 clause

import numpy


def configuration(parent_package='', top_path=None):
    """
    Generate a configuration for building extension modules.
    
    This function is used to configure the build process for extension modules in a Python package. It sets up a configuration object for building these modules using `numpy.distutils.misc_util.Configuration`.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path for the package. Defaults to None.
    
    Returns:
    - Configuration: A configuration object that can be used to
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
