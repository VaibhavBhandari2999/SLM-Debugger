import os


def configuration(parent_package='', top_path=None):
    """
    Configuration function for the 'neighbors' package.
    
    This function is responsible for setting up the build configuration for the 'neighbors' package. It uses the `Configuration` class from `numpy.distutils.misc_util` to define and compile extensions for several key components of the package: `ball_tree`, `kd_tree`, `dist_metrics`, `typedefs`, and `quad_tree`. The function also handles the inclusion of necessary headers and libraries, particularly on POSIX systems.
    
    Parameters:
    - parent_package
    """

    import numpy
    from numpy.distutils.misc_util import Configuration

    config = Configuration('neighbors', parent_package, top_path)
    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    config.add_extension('ball_tree',
                         sources=['ball_tree.pyx'],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_extension('kd_tree',
                         sources=['kd_tree.pyx'],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_extension('dist_metrics',
                         sources=['dist_metrics.pyx'],
                         include_dirs=[numpy.get_include(),
                                       os.path.join(numpy.get_include(),
                                                    'numpy')],
                         libraries=libraries)

    config.add_extension('typedefs',
                         sources=['typedefs.pyx'],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)
    config.add_extension("quad_tree",
                         sources=["quad_tree.pyx"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)

    config.add_subpackage('tests')

    return config
