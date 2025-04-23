import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for a machine learning ensemble package.
    
    This function configures the setup for building and installing a machine learning ensemble package. It includes the necessary extensions and subpackages.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to an empty string.
    - top_path (str, optional): The top-level path. Defaults to None.
    
    Returns:
    - config (Configuration): A configuration object that includes the extension and subpackage details for the ensemble package.
    
    The function adds
    """

    config = Configuration("ensemble", parent_package, top_path)
    config.add_extension("_gradient_boosting",
                         sources=["_gradient_boosting.pyx"],
                         include_dirs=[numpy.get_include()])

    config.add_subpackage("tests")

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration().todict())
