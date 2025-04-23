# Licensed under a 3-clause BSD style license - see PYFITS.rst

import numpy as np

from ....io import fits
from . import FitsTestCase
from ....tests.helper import catch_warnings


class TestDivisionFunctions(FitsTestCase):
    """Test code units that rely on correct integer division."""

    def test_rec_from_string(self):
        """
        Test reading a binary table from a string.
        
        This function reads a binary table from a FITS file and converts it to a string. It then creates a NumPy record array from the string using a specified data type and shape.
        
        Parameters:
        None
        
        Returns:
        a1 (np.rec.array): A NumPy record array created from the string representation of the binary table data.
        """

        t1 = fits.open(self.data('tb.fits'))
        s = t1[1].data.tostring()
        a1 = np.rec.array(
            s,
            dtype=np.dtype([('c1', '>i4'), ('c2', '|S3'),
                            ('c3', '>f4'), ('c4', '|i1')]),
            shape=len(s) // 12)

    def test_card_with_continue(self):
        h = fits.PrimaryHDU()
        with catch_warnings() as w:
            h.header['abc'] = 'abcdefg' * 20
        assert len(w) == 0

    def test_valid_hdu_size(self):
        t1 = fits.open(self.data('tb.fits'))
        assert type(t1[1].size) is type(1)  # nopep8

    def test_hdu_get_size(self):
        with catch_warnings() as w:
            t1 = fits.open(self.data('tb.fits'))
        assert len(w) == 0

    def test_section(self, capsys):
        """
        Test the section attribute of a FITS HDU.
        
        Parameters:
        capsys (object): Pytest fixture to capture output.
        
        This function tests the section attribute of a FITS HDU by accessing a specific element in the array. It uses the `fits.open` function to open a FITS file and then checks if the element at the specified indices (3, 2, 5) in the section of the first HDU matches the expected value [357]. If the warning
        """

        # section testing
        fs = fits.open(self.data('arange.fits'))
        with catch_warnings() as w:
            assert np.all(fs[0].section[3, 2, 5] == np.array([357]))
            assert len(w) == 0
atch_warnings() as w:
            assert np.all(fs[0].section[3, 2, 5] == np.array([357]))
            assert len(w) == 0
