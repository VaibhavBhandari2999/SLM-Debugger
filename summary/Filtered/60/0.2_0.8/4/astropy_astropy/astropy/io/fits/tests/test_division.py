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
        Test function to check if a FITS header card with a long string is handled correctly without raising a warning.
        
        This function creates a FITS PrimaryHDU object and attempts to set a header card with a very long string. The function uses a context manager to catch any warnings that might be generated during this process. If no warnings are raised, the test passes.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If a warning is caught during the process.
        
        Usage:
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
        
        This function opens a FITS file using `fits.open` and checks for any warnings
        during the process. It ensures that no warnings are generated when opening the
        file.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any warnings are generated during the file opening process.
        
        Notes:
        The function uses a context manager to capture any warnings that might be
        issued during the file opening process. It
        """

        with catch_warnings() as w:
            t1 = fits.open(self.data('tb.fits'))
        assert len(w) == 0

    def test_section(self, capsys):
        """
        Test the section attribute of a FITS HDU.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture used to capture output.
        
        This function tests the section attribute of a FITS HDU by accessing a specific element in the array stored in the HDU. It uses the `fits.open` function to open a FITS file and then accesses the section attribute to retrieve a specific element from the array. The function also uses a `catch_warnings` context manager to ensure that no warnings are
        """

        # section testing
        fs = fits.open(self.data('arange.fits'))
        with catch_warnings() as w:
            assert np.all(fs[0].section[3, 2, 5] == np.array([357]))
            assert len(w) == 0
