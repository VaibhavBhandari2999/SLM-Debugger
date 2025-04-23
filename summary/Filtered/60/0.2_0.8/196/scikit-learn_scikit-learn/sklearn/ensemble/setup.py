import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for the ensemble module.
    
    This function configures the setup for the ensemble module, including adding extensions for gradient boosting and histogram-based gradient boosting, and subpackages for tests and histogram-based gradient boosting tests.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to an empty string.
    - top_path (str, optional): The top path. Defaults to None.
    
    Returns:
    - Configuration: A configuration object for the ensemble module, containing the specified extensions and sub
    """

    config = Configuration("ensemble", parent_package, top_path)

    config.add_extension("_gradient_boosting",
                         sources=["_gradient_boosting.pyx"],
                         include_dirs=[numpy.get_include()])

    config.add_subpackage("tests")

    # Histogram-based gradient boosting files
    config.add_extension(
        "_hist_gradient_boosting._gradient_boosting",
        sources=["_hist_gradient_boosting/_gradient_boosting.pyx"],
        include_dirs=[numpy.get_include()])

    config.add_extension("_hist_gradient_boosting.histogram",
                         sources=["_hist_gradient_boosting/histogram.pyx"],
                         include_dirs=[numpy.get_include()])

    config.add_extension("_hist_gradient_boosting.splitting",
                         sources=["_hist_gradient_boosting/splitting.pyx"],
                         include_dirs=[numpy.get_include()])

    config.add_extension("_hist_gradient_boosting._binning",
                         sources=["_hist_gradient_boosting/_binning.pyx"],
                         include_dirs=[numpy.get_include()])

    config.add_extension("_hist_gradient_boosting._predictor",
                         sources=["_hist_gradient_boosting/_predictor.pyx"],
                         include_dirs=[numpy.get_include()])

    config.add_extension("_hist_gradient_boosting._loss",
                         sources=["_hist_gradient_boosting/_loss.pyx"],
                         include_dirs=[numpy.get_include()])

    config.add_extension("_hist_gradient_boosting.types",
                         sources=["_hist_gradient_boosting/types.pyx"],
                         include_dirs=[numpy.get_include()])

    config.add_extension("_hist_gradient_boosting.utils",
                         sources=["_hist_gradient_boosting/utils.pyx"],
                         include_dirs=[numpy.get_include()])

    config.add_subpackage("_hist_gradient_boosting.tests")

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration().todict())
