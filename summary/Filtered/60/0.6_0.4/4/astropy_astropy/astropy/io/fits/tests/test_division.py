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
        Test function for handling card values in FITS headers.
        
        This function tests the behavior of setting a header card value that exceeds the maximum allowed length. The function uses a `PrimaryHDU` object from the `fits` module to create a primary header unit. It attempts to set a header card with a value that is 20 times longer than the maximum allowed length for a single card. The function then checks if any warnings are raised during this operation.
        
        Parameters:
        None
        
        Returns:
        """

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
        # section testing
        fs = fits.open(self.data('arange.fits'))
        with catch_warnings() as w:
            assert np.all(fs[0].section[3, 2, 5] == np.array([357]))
            assert len(w) == 0
) == 0
