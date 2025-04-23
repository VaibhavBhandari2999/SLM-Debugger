# Licensed under a 3-clause BSD style license - see LICENSE.rst


import os
import signal
import gzip

import pytest
import numpy as np
from numpy.testing import assert_equal

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from ....tests.helper import catch_warnings
from .. import util
from ..util import ignore_sigint, _rstrip_inplace
from .._numpy_hacks import realign_dtype

from . import FitsTestCase


class TestUtils(FitsTestCase):
    @pytest.mark.skipif("sys.platform.startswith('win')")
    def test_ignore_sigint(self):
        """
        Function to test the behavior of the `ignore_sigint` decorator.
        
        This function tests the `ignore_sigint` decorator by defining a test function that sends a SIGINT signal to its own process twice. The decorator is expected to ignore the first SIGINT and only raise a `KeyboardInterrupt` after the test function completes. The test function also catches and asserts that exactly two `UserWarning` instances are raised, each indicating that the `KeyboardInterrupt` was ignored.
        
        Parameters:
        None
        
        Returns
        """

        @ignore_sigint
        def test():
            with catch_warnings(UserWarning) as w:
                pid = os.getpid()
                os.kill(pid, signal.SIGINT)
                # One more time, for good measure
                os.kill(pid, signal.SIGINT)
            assert len(w) == 2
            assert (str(w[0].message) ==
                    'KeyboardInterrupt ignored until test is complete!')

        pytest.raises(KeyboardInterrupt, test)

    def test_realign_dtype(self):
        """
        Tests a few corner-cases for the realign_dtype hack.

        These are unlikely to come in practice given how this is currently
        used in astropy.io.fits, but nonetheless tests for bugs that were
        present in earlier versions of the function.
        """

        dt = np.dtype([('a', np.int32), ('b', np.int16)])
        dt2 = realign_dtype(dt, [0, 0])
        assert dt2.itemsize == 4

        dt2 = realign_dtype(dt, [0, 1])
        assert dt2.itemsize == 4

        dt2 = realign_dtype(dt, [1, 0])
        assert dt2.itemsize == 5

        dt = np.dtype([('a', np.float64), ('b', np.int8), ('c', np.int8)])
        dt2 = realign_dtype(dt, [0, 0, 0])
        assert dt2.itemsize == 8

        dt2 = realign_dtype(dt, [0, 0, 1])
        assert dt2.itemsize == 8

        dt2 = realign_dtype(dt, [0, 0, 27])
        assert dt2.itemsize == 28


class TestUtilMode(FitsTestCase):
    """
    The high-level tests are partially covered by
    test_core.TestConvenienceFunctions.test_fileobj_mode_guessing
    but added some low-level tests as well.
    """

    def test_mode_strings(self):
        """
        Test the file mode strings.
        
        This function checks if the file mode string correctly returns None when
        the input is a string representing a file path, indicating that the file
        has not been opened yet.
        
        Parameters:
        mode (str): The file mode string, typically a file path.
        
        Returns:
        None: If the input is a string, indicating the file is not yet opened.
        """

        # A string signals that the file should be opened so the function
        # should return None, because it's simply not opened yet.
        assert util.fileobj_mode('tmp1.fits') is None

    @pytest.mark.skipif("not HAS_PIL")
    def test_mode_pil_image(self):
        """
        Test the mode of a PIL image created from a NumPy array.
        
        This function creates a random RGB image using a NumPy array, converts it to a PIL image, and saves it to a temporary file. It then checks the file mode of the saved image to ensure it is in binary read mode ('rb'), as PIL does not support append mode.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Generate a random 5x5 RGB image using NumPy.
        2
        """

        img = np.random.randint(0, 255, (5, 5, 3)).astype(np.uint8)
        result = Image.fromarray(img)

        result.save(self.temp('test_simple.jpg'))
        # PIL doesn't support append mode. So it will allways use binary read.
        with Image.open(self.temp('test_simple.jpg')) as fileobj:
            assert util.fileobj_mode(fileobj) == 'rb'

    def test_mode_gzip(self):
        # Open a gzip in every possible (gzip is binary or "touch" only) way
        # and check if the mode was correctly identified.

        # The lists consist of tuples: filenumber, given mode, identified mode
        # The filenumber must be given because read expects the file to exist
        # and x expects it to NOT exist.
        num_mode_resmode = [(0, 'a', 'ab'), (0, 'ab', 'ab'),
                            (0, 'w', 'wb'), (0, 'wb', 'wb'),
                            (1, 'x', 'xb'),
                            (1, 'r', 'rb'), (1, 'rb', 'rb')]

        for num, mode, res in num_mode_resmode:
            filename = self.temp('test{0}.gz'.format(num))
            with gzip.GzipFile(filename, mode) as fileobj:
                assert util.fileobj_mode(fileobj) == res

    def test_mode_normal_buffering(self):
        # Use the python IO with buffering parameter. Binary mode only:

        # see "test_mode_gzip" for explanation of tuple meanings.
        num_mode_resmode = [(0, 'ab', 'ab'),
                            (0, 'wb', 'wb'),
                            (1, 'xb', 'xb'),
                            (1, 'rb', 'rb')]
        for num, mode, res in num_mode_resmode:
            filename = self.temp('test1{0}.dat'.format(num))
            with open(filename, mode, buffering=0) as fileobj:
                assert util.fileobj_mode(fileobj) == res

    def test_mode_normal_no_buffering(self):
        """
        Test file mode handling in Python IO without buffering.
        
        This test checks the mode of file objects opened in various modes ('a', 'ab', 'w', 'wb', 'x', 'r', 'rb') without buffering. The function iterates over a list of tuples, each containing a number, a mode string, and a resulting expected mode string. For each tuple, it opens a temporary file with the specified mode and checks if the mode of the file object matches the expected result.
        
        Parameters
        """

        # Python IO without buffering

        # see "test_mode_gzip" for explanation of tuple meanings.
        num_mode_resmode = [(0, 'a', 'a'), (0, 'ab', 'ab'),
                            (0, 'w', 'w'), (0, 'wb', 'wb'),
                            (1, 'x', 'x'),
                            (1, 'r', 'r'), (1, 'rb', 'rb')]
        for num, mode, res in num_mode_resmode:
            filename = self.temp('test2{0}.dat'.format(num))
            with open(filename, mode) as fileobj:
                assert util.fileobj_mode(fileobj) == res

    def test_mode_normalization(self):
        # Use the normal python IO in append mode with all possible permutation
        # of the "mode" letters.

        # Tuple gives a file name suffix, the given mode and the functions
        # return. The filenumber is only for consistency with the other
        # test functions. Append can deal with existing and not existing files.
        for num, mode, res in [(0, 'a', 'a'),
                               (0, 'a+', 'a+'),
                               (0, 'ab', 'ab'),
                               (0, 'a+b', 'ab+'),
                               (0, 'ab+', 'ab+')]:
            filename = self.temp('test3{0}.dat'.format(num))
            with open(filename, mode) as fileobj:
                assert util.fileobj_mode(fileobj) == res


def test_rstrip_inplace():

    # Incorrect type
    s = np.array([1, 2, 3])
    with pytest.raises(TypeError) as exc:
        _rstrip_inplace(s)
    assert exc.value.args[0] == 'This function can only be used on string arrays'

    # Bytes array
    s = np.array(['a ', ' b', ' c c   '], dtype='S6')
    _rstrip_inplace(s)
    assert_equal(s, np.array(['a', ' b', ' c c'], dtype='S6'))

    # Unicode array
    s = np.array(['a ', ' b', ' c c   '], dtype='U6')
    _rstrip_inplace(s)
    assert_equal(s, np.array(['a', ' b', ' c c'], dtype='U6'))

    # 2-dimensional array
    s = np.array([['a ', ' b'], [' c c   ', ' a ']], dtype='S6')
    _rstrip_inplace(s)
    assert_equal(s, np.array([['a', ' b'], [' c c', ' a']], dtype='S6'))

    # 3-dimensional array
    s = np.repeat(' a a ', 24).reshape((2, 3, 4))
    _rstrip_inplace(s)
    assert_equal(s, ' a a')

    # 3-dimensional non-contiguous array
    s = np.repeat(' a a ', 1000).reshape((10, 10, 10))[:2, :3, :4]
    _rstrip_inplace(s)
    assert_equal(s, ' a a')
qual(s, ' a a')
s, ' a a')

    # 3-dimensional non-contiguous array
    s = np.repeat(' a a ', 1000).reshape((10, 10, 10))[:2, :3, :4]
    _rstrip_inplace(s)
    assert_equal(s, ' a a')
