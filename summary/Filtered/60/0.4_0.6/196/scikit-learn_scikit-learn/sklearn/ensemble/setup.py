import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for a machine learning package.
    
    This function is used to configure the setup process for a machine learning package. It includes the necessary extensions and subpackages for the package.
    
    Parameters:
    - parent_package (str, optional): The name of the parent package. Defaults to an empty string.
    - top_path (str, optional): The top-level path of the package. Defaults to None.
    
    Returns:
    - config (Configuration): A configuration object that includes extensions and subpackages for the package.
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
