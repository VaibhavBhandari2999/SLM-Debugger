# Licensed under a 3-clause BSD style license - see LICENSE.rst


def get_package_data():
    """
    Return a dictionary specifying package data for Astropy tests.
    
    This function returns a dictionary that is used to specify package data
    for the Astropy tests. The key 'astropy.tests' is used to map to a list
    containing the filename 'coveragerc'.
    
    Returns
    -------
    dict
    A dictionary specifying package data for the Astropy tests.
    """

    return {
        'astropy.tests': ['coveragerc'],
    }
