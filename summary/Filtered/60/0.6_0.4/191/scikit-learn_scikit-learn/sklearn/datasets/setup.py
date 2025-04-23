
import numpy
import os
import platform


def configuration(parent_package='', top_path=None):
    """
    Generate a configuration for the datasets package.
    
    This function configures the datasets package for building and installation using `numpy.distutils`. It sets up the necessary directories for data, descriptions, images, and test data. Additionally, it compiles a Cython extension for handling _svmlight_format if the Python implementation is not PyPy. The function also adds a subpackage for tests.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to ''.
    - top_path (
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
