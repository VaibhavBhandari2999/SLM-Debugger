# Licensed under a 3-clause BSD style license - see PYFITS.rst

import numpy as np

from ....io import fits
from . import FitsTestCase
from ....tests.helper import catch_warnings


class TestDivisionFunctions(FitsTestCase):
    """Test code units that rely on correct integer division."""

    def test_rec_from_string(self):
        t1 = fits.open(self.data('tb.fits'))
        s = t1[1].data.tostring()
        a1 = np.rec.array(
            s,
            dtype=np.dtype([('c1', '>i4'), ('c2', '|S3'),
                            ('c3', '>f4'), ('c4', '|i1')]),
            shape=len(s) // 12)

    def test_card_with_continue(self):
        """
        Test function to check if a FITS header is created without warnings when a long string is assigned to a header keyword.
        
        This function creates a FITS PrimaryHDU object and attempts to set a header keyword 'abc' to a very long string 'abcdefg' * 20. It then checks if any warnings are generated during this process.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The number of warnings generated during the header assignment should be 0.
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
        Test the HDU (Header Data Unit) size retrieval function.
        
        This function checks that no warnings are raised when opening a FITS table
        file using the `fits.open` method from the `astropy.io.fits` module.
        
        Parameters:
        None
        
        Returns:
        None
        
        Notes:
        - The test uses the `catch_warnings` context manager to capture any
        warnings that may be raised during the file opening process.
        - The file being opened is specified by `self.data('tb
        """

        with catch_warnings() as w:
            t1 = fits.open(self.data('tb.fits'))
        assert len(w) == 0

    def test_section(self, capsys):
        # section testing
        fs = fits.open(self.data('arange.fits'))
        with catch_warnings() as w:
            assert np.all(fs[0].section[3, 2, 5] == np.array([357]))
            assert len(w) == 0
