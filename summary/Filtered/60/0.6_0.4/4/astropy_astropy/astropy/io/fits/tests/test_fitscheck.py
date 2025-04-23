# Licensed under a 3-clause BSD style license - see LICENSE.rst

import pytest
from . import FitsTestCase
from ..scripts import fitscheck
from ... import fits


class TestFitscheck(FitsTestCase):
    def test_noargs(self):
        """
        Test the behavior of the `fitscheck` main function when called with no arguments.
        
        This test checks that calling `fitscheck` with no arguments raises a `SystemExit` exception with a status code of 0, indicating that the program exits successfully after printing the help message.
        
        Parameters:
        None
        
        Returns:
        None
        """

        with pytest.raises(SystemExit) as e:
            fitscheck.main(['-h'])
        assert e.value.code == 0

    def test_missing_file(self, capsys):
        assert fitscheck.main(['missing.fits']) == 1
        stdout, stderr = capsys.readouterr()
        assert 'No such file or directory' in stderr

    def test_valid_file(self, capsys):
        """
        Test the validity of a FITS file.
        
        This function checks the validity of a FITS file using the `fitscheck` tool. It performs several checks on the file and verifies the output.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture used to capture stdout and stderr.
        
        Inputs:
        - `testfile`: The path to the FITS file to be tested.
        
        Outputs:
        - Verifies that the `fitscheck` tool returns a status code of 0 for the file
        """

        testfile = self.data('checksum.fits')

        assert fitscheck.main([testfile]) == 0
        assert fitscheck.main([testfile, '--compliance']) == 0

        assert fitscheck.main([testfile, '-v']) == 0
        stdout, stderr = capsys.readouterr()
        assert 'OK' in stderr

    def test_remove_checksums(self, capsys):
        self.copy_file('checksum.fits')
        testfile = self.temp('checksum.fits')
        assert fitscheck.main([testfile, '--checksum', 'remove']) == 1
        assert fitscheck.main([testfile]) == 1
        stdout, stderr = capsys.readouterr()
        assert 'MISSING' in stderr

    def test_no_checksums(self, capsys):
        testfile = self.data('arange.fits')

        assert fitscheck.main([testfile]) == 1
        stdout, stderr = capsys.readouterr()
        assert 'Checksum not found' in stderr

        assert fitscheck.main([testfile, '--ignore-missing']) == 0
        stdout, stderr = capsys.readouterr()
        assert stderr == ''

    def test_overwrite_invalid(self, capsys):
        """
        Tests that invalid checksum or datasum are overwriten when the file is
        saved.
        """
        reffile = self.temp('ref.fits')
        with fits.open(self.data('tb.fits')) as hdul:
            hdul.writeto(reffile, checksum=True)

        # replace checksums with wrong ones
        testfile = self.temp('test.fits')
        with fits.open(self.data('tb.fits')) as hdul:
            hdul[0].header['DATASUM'] = '1       '
            hdul[0].header['CHECKSUM'] = '8UgqATfo7TfoATfo'
            hdul[1].header['DATASUM'] = '2349680925'
            hdul[1].header['CHECKSUM'] = '11daD8bX98baA8bU'
            hdul.writeto(testfile)

        assert fitscheck.main([testfile]) == 1
        stdout, stderr = capsys.readouterr()
        assert 'BAD' in stderr
        assert 'Checksum verification failed' in stderr

        assert fitscheck.main([testfile, '--write', '--force']) == 1
        stdout, stderr = capsys.readouterr()
        assert 'BAD' in stderr

        # check that the file was fixed
        assert fitscheck.main([testfile]) == 0
