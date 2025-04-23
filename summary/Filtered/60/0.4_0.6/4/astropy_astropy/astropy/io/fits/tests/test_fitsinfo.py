# Licensed under a 3-clause BSD style license - see LICENSE.rst

from . import FitsTestCase
from ..scripts import fitsinfo


class TestFitsinfo(FitsTestCase):

    def test_onefile(self, capsys):
        """
        Test the 'fitsinfo.main' function with a single FITS file.
        
        This test function runs the 'fitsinfo.main' function with a specified FITS file and captures the output. It then checks the output to ensure it contains the expected number of lines and that the lines contain the correct information about the FITS file.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture that captures stdout and stderr.
        
        Input:
        - A single FITS file path provided as an argument to 'fits
        """

        fitsinfo.main([self.data('arange.fits')])
        out, err = capsys.readouterr()
        out = out.splitlines()
        assert len(out) == 3
        assert out[1].startswith(
            'No.    Name      Ver    Type      Cards   Dimensions   Format')
        assert out[2].startswith(
            '  0  PRIMARY       1 PrimaryHDU       7   (11, 10, 7)   int32')

    def test_multiplefiles(self, capsys):
        """
        Tests the functionality of the `fitsinfo.main` function when multiple FITS files are provided.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture that captures output from the test.
        
        Key Parameters:
        - `self`: The test class instance, providing access to the test's setup and data.
        - `capsys`: A pytest fixture used to capture the output and errors from the test.
        
        Inputs:
        - Two FITS files: 'arange.fits' and 'ascii.fits'
        """

        fitsinfo.main([self.data('arange.fits'),
                       self.data('ascii.fits')])
        out, err = capsys.readouterr()
        out = out.splitlines()
        assert len(out) == 8
        assert out[1].startswith(
            'No.    Name      Ver    Type      Cards   Dimensions   Format')
        assert out[2].startswith(
            '  0  PRIMARY       1 PrimaryHDU       7   (11, 10, 7)   int32')
        assert out[3] == ''
        assert out[7].startswith(
            '  1                1 TableHDU        20   5R x 2C   [E10.4, I5]')
