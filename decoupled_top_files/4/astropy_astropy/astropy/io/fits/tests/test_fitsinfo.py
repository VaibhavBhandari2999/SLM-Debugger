# Licensed under a 3-clause BSD style license - see LICENSE.rst

from . import FitsTestCase
from ..scripts import fitsinfo


class TestFitsinfo(FitsTestCase):

    def test_onefile(self, capsys):
        """
        Test the `fitsinfo.main` function with a single FITS file.
        
        Args:
        capsys: A pytest fixture for capturing stdout and stderr.
        
        Summary:
        This function tests the `fitsinfo.main` function by passing a single FITS file ('arange.fits') as an argument. It captures the output and checks that the output contains exactly three lines, with the second line starting with the header information and the third line indicating the details of the primary HDU (including its type
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
        Test the `fitsinfo.main` function with multiple FITS files.
        
        This test case verifies that the `fitsinfo.main` function correctly processes and outputs information for multiple FITS files. The function is called with two file paths: 'arange.fits' and 'ascii.fits'. The expected output is captured and compared against predefined assertions.
        
        Args:
        capsys: A pytest fixture for capturing stdout and stderr.
        
        Returns:
        None
        
        Raises:
        AssertionError: If the output does
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
