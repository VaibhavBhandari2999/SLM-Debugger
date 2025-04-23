import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for a Python package.
    
    This function is used to configure the setup process for a Python package, particularly for extensions that need to be compiled. It includes the addition of an extension module and a subpackage for testing.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path of the package. Defaults to None.
    
    Returns:
    - config (Configuration): A configuration object
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
