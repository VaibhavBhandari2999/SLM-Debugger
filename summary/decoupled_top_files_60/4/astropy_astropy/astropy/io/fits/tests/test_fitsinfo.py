# Licensed under a 3-clause BSD style license - see LICENSE.rst

from . import FitsTestCase
from ..scripts import fitsinfo


class TestFitsinfo(FitsTestCase):

    def test_onefile(self, capsys):
        """
        Test the `fitsinfo.main` function with a single FITS file.
        
        This function tests the `fitsinfo.main` function by passing a single FITS file and captures the output. It then checks the number of lines in the output and verifies that the output contains the expected header information.
        
        Parameters:
        capsys: A fixture provided by pytest for capturing stdout and stderr.
        
        Returns:
        None: This function does not return any value. It asserts the correctness of the output.
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
        Test the functionality of the `fitsinfo.main` function when multiple FITS files are provided.
        
        This test case checks the output of the `fitsinfo.main` function when it is called with two FITS files: 'arange.fits' and 'ascii.fits'. The expected output is verified by comparing the number of lines in the output and specific lines that contain information about the files.
        
        Parameters:
        - capsys: A fixture provided by pytest-capturelog that captures stdout and stderr.
        
        Returns:
        -
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
