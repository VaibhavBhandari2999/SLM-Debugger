import os

from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for a Python package.
    
    This function is typically used in the setup.py file of a Python package to configure its setup process. It sets up the package's metadata and extensions, and adds subpackages and extensions to it.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path of the package. Defaults to None.
    
    Returns:
    - config (Configuration): A configuration
    """

    config = Configuration("metrics", parent_package, top_path)

    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    config.add_subpackage('cluster')

    config.add_extension("pairwise_fast",
                         sources=["pairwise_fast.pyx"],
                         libraries=libraries)

    config.add_subpackage('tests')

    return config


if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration().todict())
