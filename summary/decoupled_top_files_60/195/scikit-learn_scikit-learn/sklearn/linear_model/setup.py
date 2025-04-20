import os

import numpy

from Cython import Tempita

def configuration(parent_package='', top_path=None):
    """
    Generates a configuration for building the linear model package.
    
    This function configures the build process for the linear model package. It sets up the necessary extensions and subpackages for building the package. The function takes two optional parameters:
    
    - `parent_package`: The name of the parent package, if any. Default is an empty string.
    - `top_path`: The top-level path for the package. Default is `None`.
    
    Key Parameters:
    - `parent_package` (str): The name of the parent
    """

    from numpy.distutils.misc_util import Configuration

    config = Configuration('linear_model', parent_package, top_path)

    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    config.add_extension('cd_fast',
                         sources=['cd_fast.pyx'],
                         include_dirs=numpy.get_include(),
                         libraries=libraries)

    config.add_extension('sgd_fast',
                         sources=['sgd_fast.pyx'],
                         include_dirs=numpy.get_include(),
                         libraries=libraries)

    # generate sag_fast from template
    sag_cython_file = 'sklearn/linear_model/sag_fast.pyx.tp'
    sag_file = sag_cython_file.replace('.tp', '')

    if not (os.path.exists(sag_file) and
            os.stat(sag_cython_file).st_mtime < os.stat(sag_file).st_mtime):

        with open(sag_cython_file, "r") as f:
            tmpl = f.read()
        tmpl_ = Tempita.sub(tmpl)

        with open(sag_file, "w") as f:
            f.write(tmpl_)

    config.add_extension('sag_fast',
                         sources=['sag_fast.pyx'],
                         include_dirs=numpy.get_include())

    # add other directories
    config.add_subpackage('tests')

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
