# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

import os

import pytest
import numpy as np

from astropy.io import fits

asdf = pytest.importorskip('asdf')
from asdf.tests import helpers


def test_complex_structure(tmpdir):
    """
    Test writing a FITS file with a complex structure.
    
    This function tests the round-trip functionality for a FITS file with a complex structure. The file is read from a predefined location and then written back to a temporary directory. The function compares the original and the written file to ensure they are identical.
    
    Parameters:
    tmpdir (py.path.local): A temporary directory object where the FITS file will be written.
    
    Returns:
    None: The function asserts that the round-trip operation is successful
    """

    with fits.open(os.path.join(
            os.path.dirname(__file__), 'data', 'complex.fits'), memmap=False) as hdulist:
        tree = {
            'fits': hdulist
            }

        helpers.assert_roundtrip_tree(tree, tmpdir)


def test_fits_table(tmpdir):
    """
    Test if a FITS binary table can be correctly round-tripped through YAML.
    
    Parameters:
    tmpdir (py.path.local): A temporary directory object where the round-tripped file is saved.
    
    This function creates a FITS binary table with two columns 'A' and 'B', each of integer type. It then appends this table to a HDUList and stores it in a dictionary. The function checks if the table is correctly represented in the YAML format by verifying the presence of the '
    """

    a = np.array(
        [(0, 1), (2, 3)],
        dtype=[(str('A'), int), (str('B'), int)])

    h = fits.HDUList()
    h.append(fits.BinTableHDU.from_columns(a))
    tree = {'fits': h}

    def check_yaml(content):
        assert b'!core/table' in content

    helpers.assert_roundtrip_tree(tree, tmpdir, raw_yaml_check_func=check_yaml)
