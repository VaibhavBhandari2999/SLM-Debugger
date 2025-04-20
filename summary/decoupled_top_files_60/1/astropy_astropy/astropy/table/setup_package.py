# Licensed under a 3-clause BSD style license - see LICENSE.rst

import os

import numpy
from setuptools import Extension

ROOT = os.path.relpath(os.path.dirname(__file__))


def get_extensions():
    """
    Generates a list of Cython extensions for the Astropy Table module.
    
    This function compiles a list of Cython extensions for the Astropy Table module. Each extension corresponds to a specific source file and is configured with the necessary include directories.
    
    Parameters:
    None
    
    Returns:
    list: A list of `Extension` objects, each representing a Cython extension for the Astropy Table module.
    """

    sources = ["_np_utils.pyx", "_column_mixins.pyx"]
    include_dirs = [numpy.get_include()]

    exts = [
        Extension(
            name="astropy.table." + os.path.splitext(source)[0],
            sources=[os.path.join(ROOT, source)],
            include_dirs=include_dirs,
        )
        for source in sources
    ]

    return exts
