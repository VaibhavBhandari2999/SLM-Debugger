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
        """
        Test the `fitsdiff.main()` function without any arguments.
        
        This test checks that the `fitsdiff.main()` function raises a `SystemExit` exception with a status code of 2 when called without any arguments.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        pytest.exceptions.ExceptionInfo: Captured exception information.
        
        Notes:
        - The test uses the `pytest.raises` context manager to capture the exception.
        - The expected exception is `SystemExit` with a status code of 2.
        """

        with pytest.raises(SystemExit) as e:
            fitsdiff.main()
        assert e.value.code == 2

    def test_oneargargs(self):
        with pytest.raises(SystemExit) as e:
            fitsdiff.main(["file1"])
        assert e.value.code == 2

    def test_nodiff(self):
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
        """
        Test the quiet mode of the fitsdiff tool.
        
        This function checks if the fitsdiff tool runs in quiet mode without producing any output. It creates two FITS files with identical data, writes the data to these files, and then uses fitsdiff with the -q option to compare the files. The function asserts that the comparison returns 0 (indicating no differences) and that no output or error messages are printed to the console.
        
        Parameters:
        capsys (pytest fixture): A pytest fixture that
        """

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
