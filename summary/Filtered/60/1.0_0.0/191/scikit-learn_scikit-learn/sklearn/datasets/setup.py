
import numpy
import os
import platform


def configuration(parent_package='', top_path=None):
    """
    Generate a configuration for a Python package.
    
    This function configures the setup for a Python package named 'datasets'. It sets up the necessary components for building and installing the package, including data directories, extensions, and subpackages.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path for the package. Defaults to None.
    
    Returns:
    - Configuration: An instance of the Configuration class from
    """

    from numpy.distutils.misc_util import Configuration
    config = Configuration('datasets', parent_package, top_path)
    config.add_data_dir('data')
    config.add_data_dir('descr')
    config.add_data_dir('images')
    config.add_data_dir(os.path.join('tests', 'data'))
    if platform.python_implementation() != 'PyPy':
        config.add_extension('_svmlight_format',
                             sources=['_svmlight_format.pyx'],
                             include_dirs=[numpy.get_include()])
    config.add_subpackage('tests')
    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
