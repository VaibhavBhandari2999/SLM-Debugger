# Licensed under a 3-clause BSD style license - see PYFITS.rst

import numpy as np

from ....io import fits
from . import FitsTestCase
from ....tests.helper import catch_warnings


class TestDivisionFunctions(FitsTestCase):
    """Test code units that rely on correct integer division."""

    def test_rec_from_string(self):
        """
        Test reading a table HDU from a FITS file using the `tostring` method.
        
        This function reads a binary table from a FITS file, converts it to a string, and then reconstructs it into a NumPy record array.
        
        Parameters:
        None
        
        Returns:
        a1 (np.rec.array): A NumPy record array containing the data from the FITS file, reconstructed from the string representation.
        """

        t1 = fits.open(self.data('tb.fits'))
        s = t1[1].data.tostring()
        a1 = np.rec.array(
            s,
            dtype=np.dtype([('c1', '>i4'), ('c2', '|S3'),
                            ('c3', '>f4'), ('c4', '|i1')]),
            shape=len(s) // 12)

    def test_card_with_continue(self):
        """
        Tests the behavior of a FITS header when a warning is triggered due to a header keyword value exceeding the maximum allowed length.
        
        This function creates a FITS PrimaryHDU and attempts to set a header keyword ('abc') with a value that exceeds the maximum allowed length. If the length of the value is within the allowed limit, no warning should be raised.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The number of warnings issued during the header setting should be 0.
        """

        h = fits.PrimaryHDU()
        with catch_warnings() as w:
            h.header['abc'] = 'abcdefg' * 20
        assert len(w) == 0

    def test_valid_hdu_size(self):
        t1 = fits.open(self.data('tb.fits'))
        assert type(t1[1].size) is type(1)  # nopep8

    def test_hdu_get_size(self):
        """
        Test the HDU (Header Data Unit) get_size method.
        
        This function checks the get_size method of an HDU object by opening a FITS
        table file and verifying that no warnings are issued during the process.
        
        Parameters:
        None
        
        Returns:
        None
        
        Notes:
        - The function uses the `fits.open` method from the `astropy.io.fits`
        module to open the 'tb.fits' file located in the 'data' directory.
        - It uses a context manager
        """

        with catch_warnings() as w:
            t1 = fits.open(self.data('tb.fits'))
        assert len(w) == 0

    def test_section(self, capsys):
        """
        Test the section attribute of a FITS HDU.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture used to capture output.
        
        This function tests the section attribute of a FITS HDU by accessing a specific element in the array stored in the HDU. It uses the `fits.open` function to open a FITS file and then checks if the element at the specified indices (3, 2, 5) in the section attribute matches the expected value (357).
        """

        # section testing
        fs = fits.open(self.data('arange.fits'))
        with catch_warnings() as w:
            assert np.all(fs[0].section[3, 2, 5] == np.array([357]))
            assert len(w) == 0
