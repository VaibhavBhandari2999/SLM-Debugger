# Licensed under a 3-clause BSD style license - see LICENSE.rst

from . import FitsTestCase
from ..scripts import fitsinfo


class TestFitsinfo(FitsTestCase):

    def test_onefile(self, capsys):
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
        Test the functionality of the `fitsinfo.main` function with multiple FITS files.
        
        This test function verifies that the `fitsinfo.main` function correctly processes and displays information for multiple FITS files. It uses the `capsys` fixture to capture the output of the function and checks that the output matches the expected format and content.
        
        Parameters:
        - capsys: A fixture provided by pytest for capturing stdout and stderr.
        
        Input:
        - Two FITS files: 'arange.fits' and 'ascii
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
