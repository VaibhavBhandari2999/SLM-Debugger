import os
import platform


def configuration(parent_package='', top_path=None):
    """
    Generate a configuration for the 'feature_extraction' package.
    
    This function is used to configure the setup process for the 'feature_extraction' package. It sets up the necessary components for building and installing the package, including extensions and tests.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path for the package. Defaults to None.
    
    Returns:
    - Configuration: An instance of the Configuration class
    """

    import numpy
    from numpy.distutils.misc_util import Configuration

    config = Configuration('feature_extraction', parent_package, top_path)
    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    if platform.python_implementation() != 'PyPy':
        config.add_extension('_hashing',
                             sources=['_hashing.pyx'],
                             include_dirs=[numpy.get_include()],
                             libraries=libraries)
    config.add_subpackage("tests")

    return config
