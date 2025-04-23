# Licensed under a 3-clause BSD style license - see LICENSE.rst

import pytest
from . import FitsTestCase
from ..scripts import fitscheck
from ... import fits


class TestFitscheck(FitsTestCase):
    def test_noargs(self):
        """
        Test the behavior of the `fitscheck` main function when called with no arguments.
        
        This test ensures that calling `fitscheck.main()` with no arguments raises a `SystemExit` exception with a status code of 0, indicating a successful exit with help information.
        
        Key Parameters:
        - None
        
        Input:
        - No arguments are passed to the `fitscheck.main()` function.
        
        Output:
        - A `SystemExit` exception is raised with a status code of 0.
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
        Test the validation of a valid FITS file.
        
        This function tests the validation of a valid FITS file using the `fitscheck` tool. It checks the file for basic validation and compliance, and also verifies the verbose output.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture used to capture output from the test.
        
        Key Steps:
        1. Define the test file path using the `data` method.
        2. Validate the file using `fitscheck` without any additional options.
        3.
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
        """
        Test the behavior of the fitscheck.main function when no checksums are present in a FITS file.
        
        Parameters:
        capsys: A pytest fixture that captures stdout and stderr.
        
        This function performs the following actions:
        1. Asserts that the main function returns 1 when checksums are not found in the FITS file.
        2. Captures and asserts that the error message 'Checksum not found' is present in the stderr output.
        3. Asserts that the main function returns 0 when
        """

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
ck.main([testfile]) == 0
