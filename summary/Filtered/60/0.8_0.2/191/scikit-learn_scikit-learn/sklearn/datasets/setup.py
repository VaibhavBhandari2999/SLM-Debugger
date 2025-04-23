
import numpy
import os
import platform


def configuration(parent_package='', top_path=None):
    """
    Generate a configuration for the datasets package.
    
    This function configures the setup for the datasets package, including adding data directories, extensions, and subpackages.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to ''.
    - top_path (str, optional): The top-level path. Defaults to None.
    
    Returns:
    - Configuration: A configuration object for the datasets package, including data directories, extensions, and subpackages.
    
    Key Points:
    - Adds data directories for 'data',
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
