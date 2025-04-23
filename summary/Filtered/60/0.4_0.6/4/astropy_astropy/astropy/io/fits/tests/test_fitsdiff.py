# Licensed under a 3-clause BSD style license - see LICENSE.rst

import numpy as np
import pytest

from . import FitsTestCase
from ..hdu import PrimaryHDU
from ..scripts import fitsdiff
from ....tests.helper import catch_warnings
from ....utils.exceptions import AstropyDeprecationWarning
from ....version import version


class TestFITSDiff_script(FitsTestCase):

    def test_noargs(self):
        with pytest.raises(SystemExit) as e:
            fitsdiff.main()
        assert e.value.code == 2

    def test_oneargargs(self):
        """
        Test the `fitsdiff.main` function with a single argument.
        
        This test case checks that `fitsdiff.main` raises a `SystemExit` exception with a return code of 2 when provided with a single positional argument.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the exception raised does not match the expected `SystemExit` with code 2.
        """

        with pytest.raises(SystemExit) as e:
            fitsdiff.main(["file1"])
        assert e.value.code == 2

    def test_nodiff(self):
        """
        Test function to verify that two FITS files are identical.
        
        This function creates two FITS files from a 2D numpy array and its copy,
        writes them to temporary files, and then uses the `fitsdiff` tool to
        compare the files. The function asserts that the number of differing
        pixels (numdiff) is zero, indicating that the files are identical.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Create a 2D numpy array `a
        """

        a = np.arange(100).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a.copy()
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)
        numdiff = fitsdiff.main([tmp_a, tmp_b])
        assert numdiff == 0

    def test_onediff(self):
        a = np.arange(100).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a.copy()
        b[1, 0] = 12
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)
        numdiff = fitsdiff.main([tmp_a, tmp_b])
        assert numdiff == 1

    def test_manydiff(self, capsys):
        a = np.arange(100).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a + 1
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)

        numdiff = fitsdiff.main([tmp_a, tmp_b])
        out, err = capsys.readouterr()
        assert numdiff == 1
        assert out.splitlines()[-4:] == [
            '        a> 9',
            '        b> 10',
            '     ...',
            '     100 different pixels found (100.00% different).']

        numdiff = fitsdiff.main(['-n', '1', tmp_a, tmp_b])
        out, err = capsys.readouterr()
        assert numdiff == 1
        assert out.splitlines()[-4:] == [
            '        a> 0',
            '        b> 1',
            '     ...',
            '     100 different pixels found (100.00% different).']

    def test_outputfile(self):
        a = np.arange(100).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a.copy()
        b[1, 0] = 12
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)

        numdiff = fitsdiff.main(['-o', self.temp('diff.txt'), tmp_a, tmp_b])
        assert numdiff == 1
        with open(self.temp('diff.txt')) as f:
            out = f.read()
        assert out.splitlines()[-4:] == [
            '     Data differs at [1, 2]:',
            '        a> 10',
            '        b> 12',
            '     1 different pixels found (1.00% different).']

    def test_atol(self):
        a = np.arange(100, dtype=float).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a.copy()
        b[1, 0] = 11
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)

        numdiff = fitsdiff.main(["-a", "1", tmp_a, tmp_b])
        assert numdiff == 0

        numdiff = fitsdiff.main(["--exact", "-a", "1", tmp_a, tmp_b])
        assert numdiff == 1

    def test_rtol(self):
        a = np.arange(100, dtype=float).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a.copy()
        b[1, 0] = 11
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)
        numdiff = fitsdiff.main(["-r", "1e-1", tmp_a, tmp_b])
        assert numdiff == 0

    def test_rtol_diff(self, capsys):
        a = np.arange(100, dtype=float).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a.copy()
        b[1, 0] = 11
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)
        numdiff = fitsdiff.main(["-r", "1e-2", tmp_a, tmp_b])
        assert numdiff == 1
        out, err = capsys.readouterr()
        assert out == """
 fitsdiff: {}
 a: {}
 b: {}
 Maximum number of different data values to be reported: 10
 Relative tolerance: 0.01, Absolute tolerance: 0.0

Primary HDU:\n\n   Data contains differences:
     Data differs at [1, 2]:
        a> 10.0
         ?  ^
        b> 11.0
         ?  ^
     1 different pixels found (1.00% different).\n""".format(version, tmp_a, tmp_b)
        assert err == ""

    def test_fitsdiff_script_both_d_and_r(self, capsys):
        a = np.arange(100).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a.copy()
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)
        with catch_warnings(AstropyDeprecationWarning) as warning_lines:
            fitsdiff.main(["-r", "1e-4", "-d", "1e-2", tmp_a, tmp_b])
            # `rtol` is always ignored when `tolerance` is provided
            assert warning_lines[0].category == AstropyDeprecationWarning
            assert (str(warning_lines[0].message) ==
                    '"-d" ("--difference-tolerance") was deprecated in version 2.0 '
                    'and will be removed in a future version. '
                    'Use "-r" ("--relative-tolerance") instead.')
        out, err = capsys.readouterr()
        assert out == """
 fitsdiff: {}
 a: {}
 b: {}
 Maximum number of different data values to be reported: 10
 Relative tolerance: 0.01, Absolute tolerance: 0.0

No differences found.\n""".format(version, tmp_a, tmp_b)

    def test_wildcard(self):
        """
        Tests the behavior of the `fitsdiff` function when a wildcard character is used in the first input file path.
        
        This function checks if the `fitsdiff` function raises a `SystemExit` exception with a status code of 2 when a wildcard character (`*`) is used in the first input file path and the second input file path is provided as a string.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the `SystemExit` is not raised or the
        """

        tmp1 = self.temp("tmp_file1")
        with pytest.raises(SystemExit) as e:
            fitsdiff.main([tmp1+"*", "ACME"])
        assert e.value.code == 2

    def test_not_quiet(self, capsys):
        a = np.arange(100).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a.copy()
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)
        numdiff = fitsdiff.main([tmp_a, tmp_b])
        assert numdiff == 0
        out, err = capsys.readouterr()
        assert out == """
 fitsdiff: {}
 a: {}
 b: {}
 Maximum number of different data values to be reported: 10
 Relative tolerance: 0.0, Absolute tolerance: 0.0

No differences found.\n""".format(version, tmp_a, tmp_b)
        assert err == ""

    def test_quiet(self, capsys):
        a = np.arange(100).reshape(10, 10)
        hdu_a = PrimaryHDU(data=a)
        b = a.copy()
        hdu_b = PrimaryHDU(data=b)
        tmp_a = self.temp('testa.fits')
        tmp_b = self.temp('testb.fits')
        hdu_a.writeto(tmp_a)
        hdu_b.writeto(tmp_b)
        numdiff = fitsdiff.main(["-q", tmp_a, tmp_b])
        assert numdiff == 0
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""
)
        assert out == ""
        assert err == ""
