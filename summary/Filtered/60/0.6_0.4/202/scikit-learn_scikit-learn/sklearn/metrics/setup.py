import os

from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for a Python package.
    
    This function is used to set up the configuration for a Python package, particularly for distribution and building extensions. It includes subpackages, extensions, and tests.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path of the package. Defaults to None.
    
    Returns:
    - config (Configuration): The configuration object that contains details about the package,
    """

    config = Configuration("metrics", parent_package, top_path)

    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    config.add_subpackage('_plot')
    config.add_subpackage('_plot.tests')
    config.add_subpackage('cluster')

    config.add_extension("_pairwise_fast",
                         sources=["_pairwise_fast.pyx"],
                         libraries=libraries)

    config.add_subpackage('tests')

    return config


if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration().todict())
