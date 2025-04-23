import os

import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):
    """
    Generates a configuration for a machine learning library.
    
    This function configures the setup for building and installing the tree module of a machine learning library. It includes extensions for various components like _tree, _splitter, _criterion, and _utils, which are compiled from Cython sources. The configuration also adds test subpackages and includes necessary header files.
    
    Parameters:
    - parent_package (str, optional): The parent package name. Defaults to an empty string.
    - top_path (str, optional
    """

    config = Configuration("tree", parent_package, top_path)
    libraries = []
    if os.name == 'posix':
        libraries.append('m')
    config.add_extension("_tree",
                         sources=["_tree.pyx"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries,
                         extra_compile_args=["-O3"])
    config.add_extension("_splitter",
                         sources=["_splitter.pyx"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries,
                         extra_compile_args=["-O3"])
    config.add_extension("_criterion",
                         sources=["_criterion.pyx"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries,
                         extra_compile_args=["-O3"])
    config.add_extension("_utils",
                         sources=["_utils.pyx"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries,
                         extra_compile_args=["-O3"])

    config.add_subpackage("tests")
    config.add_data_files("_criterion.pxd")
    config.add_data_files("_splitter.pxd")
    config.add_data_files("_tree.pxd")
    config.add_data_files("_utils.pxd")

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration().todict())
