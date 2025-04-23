import os
import platform


def configuration(parent_package='', top_path=None):
    """
    Generates a configuration for a Python package related to feature extraction.
    
    This function is typically used in the setup process of a Python package, configuring how the package's modules and extensions are built. It sets up the necessary components for compiling and linking C/C++ extensions and subpackages.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path of the package. Defaults to None.
    
    Returns
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
