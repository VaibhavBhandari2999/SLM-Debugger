import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generate a scikit-learn ensemble configuration.
    
    This function configures the setup for building and testing an ensemble
    module within a scikit-learn package. It includes the following key components:
    
    - Adds an extension named "_gradient_boosting" using Cython with specified source files and include directories.
    - Adds subpackages, specifically "tests", for running tests on the ensemble module.
    
    Parameters:
    -----------
    parent_package : str, optional
    The name of the parent
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
