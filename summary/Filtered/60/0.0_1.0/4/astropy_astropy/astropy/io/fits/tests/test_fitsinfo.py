# Licensed under a 3-clause BSD style license - see LICENSE.rst

from . import FitsTestCase
from ..scripts import fitsinfo


class TestFitsinfo(FitsTestCase):

    def test_onefile(self, capsys):
        """
        Test the `fitsinfo.main` function with a single FITS file.
        
        This function tests the `fitsinfo.main` function by passing a single FITS file
        and verifying the output. The output is captured and checked to ensure it
        contains the expected number of lines and specific content.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture that captures stdout and stderr.
        
        Returns:
        None: This function does not return any value. It asserts the correctness
        of the output.
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
        Tests the `fitsinfo.main` function with multiple FITS files.
        
        This function runs the `fitsinfo.main` function on two FITS files and captures the output. The output is then checked to ensure it contains the expected number of lines and specific headers.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture that captures stdout and stderr.
        
        Key Parameters:
        - `self`: The test case instance, containing methods to access test data files.
        
        Output:
        - The function asserts that the
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
