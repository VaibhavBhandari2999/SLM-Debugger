# Licensed under a 3-clause BSD style license - see LICENSE.rst

import pytest
from . import FitsTestCase
from ..scripts import fitscheck
from ... import fits


class TestFitscheck(FitsTestCase):
    def test_noargs(self):
        with pytest.raises(SystemExit) as e:
            fitscheck.main(['-h'])
        assert e.value.code == 0

    def test_missing_file(self, capsys):
        """
        Tests the behavior of the `fitscheck.main` function when a missing file is provided as an argument.
        
        Parameters:
        capsys: A pytest fixture that captures output from the console.
        
        Returns:
        None: This function does not return any value. It asserts that the `fitscheck.main` function returns 1 when a non-existent file is passed and checks if the appropriate error message is printed.
        
        Key Points:
        - The function asserts that `fitscheck.main(['missing.fits'])` returns 1
        """

        assert fitscheck.main(['missing.fits']) == 1
        stdout, stderr = capsys.readouterr()
        assert 'No such file or directory' in stderr

    def test_valid_file(self, capsys):
        """
        Test the validation of a valid FITS file using the fitscheck utility.
        
        This function tests the validation of a FITS file named 'checksum.fits' using the fitscheck utility. It checks the file for compliance and prints verbose output.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture used to capture stdout and stderr.
        
        Returns:
        None: This function does not return any value. It asserts that the fitscheck utility returns 0 for both standard and compliance checks and prints 'OK'
        """

        testfile = self.data('checksum.fits')

        assert fitscheck.main([testfile]) == 0
        assert fitscheck.main([testfile, '--compliance']) == 0

        assert fitscheck.main([testfile, '-v']) == 0
        stdout, stderr = capsys.readouterr()
        assert 'OK' in stderr

    def test_remove_checksums(self, capsys):
        """
        Test the functionality of the `fitscheck` command to remove checksums from a FITS file.
        
        This function performs the following steps:
        1. Copies a FITS file named 'checksum.fits' to a temporary file.
        2. Runs the `fitscheck` command with the `--checksum remove` option on the temporary file and asserts that the return code is 1.
        3. Runs the `fitscheck` command without any options on the temporary file and asserts that the return code is 1
        """

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
