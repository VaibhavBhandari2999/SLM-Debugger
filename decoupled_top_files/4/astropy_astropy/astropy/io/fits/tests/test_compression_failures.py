# Licensed under a 3-clause BSD style license - see PYFITS.rst

import pytest
import numpy as np

from ....io import fits
from ..compression import compress_hdu

from . import FitsTestCase


MAX_INT = np.iinfo(np.intc).max
MAX_LONG = np.iinfo(np.long).max
MAX_LONGLONG = np.iinfo(np.longlong).max


class TestCompressionFunction(FitsTestCase):
    def test_wrong_argument_number(self):
        with pytest.raises(TypeError):
            compress_hdu(1, 2)

    def test_unknown_compression_type(self):
        """
        Raises a ValueError when attempting to compress an HDU with an unrecognized compression type.
        
        This function tests the behavior of the `compress_hdu` function when given an `CompImageHDU` object with an unsupported compression type specified in its header.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the compression type is unrecognized.
        
        Functions Used:
        - `fits.CompImageHDU`: Creates a compressed image HDU.
        - `pytest.raises
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header['ZCMPTYPE'] = 'fun'
        with pytest.raises(ValueError) as exc:
            compress_hdu(hdu)
        assert 'Unrecognized compression type: fun' in str(exc)

    def test_zbitpix_unknown(self):
        """
        Test the behavior of the `compress_hdu` function when an unsupported ZBITPIX value is specified.
        
        Summary:
        This test function checks how the `compress_hdu` function handles an unsupported ZBITPIX value (13 in this case) by creating a CompImageHDU object with a specific ZBITPIX header keyword set to 13. It then asserts that a ValueError is raised with the expected error message containing the invalid BITPIX value.
        
        Parameters:
        None
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header['ZBITPIX'] = 13
        with pytest.raises(ValueError) as exc:
            compress_hdu(hdu)
        assert 'Invalid value for BITPIX: 13' in str(exc)

    def test_data_none(self):
        """
        Test that an error is raised when attempting to compress a CompImageHDU with data set to None.
        
        This function creates a CompImageHDU with a numpy array of ones, sets its data attribute to None, and then attempts to compress it using the `compress_hdu` function. It asserts that a TypeError is raised with a specific message indicating that the data must be a numpy.ndarray.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If the
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu.data = None
        with pytest.raises(TypeError) as exc:
            compress_hdu(hdu)
        assert 'CompImageHDU.data must be a numpy.ndarray' in str(exc)

    def test_missing_internal_header(self):
        """
        Test that an AttributeError is raised when attempting to compress an HDU with missing internal header.
        
        This function creates a `CompImageHDU` object with a 10x10 array of ones, deletes its internal header, and then attempts to compress the HDU using the `compress_hdu` function. An `AttributeError` is expected to be raised due to the missing header, and the test verifies that the error message contains the string '_header'.
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        del hdu._header
        with pytest.raises(AttributeError) as exc:
            compress_hdu(hdu)
        assert '_header' in str(exc)

    def test_invalid_tform(self):
        """
        Test invalid TFORM value.
        
        This function tests the behavior of the `compress_hdu` function when an invalid
        TFORM value is set in the header of a CompImageHDU object. It sets the TFORM1
        keyword to an invalid value ('TX') and expects a RuntimeError to be raised.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        - RuntimeError: If the invalid TFORM value does not trigger a runtime error.
        
        Important Functions
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header['TFORM1'] = 'TX'
        with pytest.raises(RuntimeError) as exc:
            compress_hdu(hdu)
        assert 'TX' in str(exc) and 'TFORM' in str(exc)

    def test_invalid_zdither(self):
        """
        Test invalid ZDITHER0 value.
        
        This function tests the behavior of the `compress_hdu` function when an invalid
        ZDITHER0 value is set in a CompImageHDU object. The ZDITHER0 header keyword is
        set to an invalid type ('a' instead of an integer), and an exception of type
        TypeError is expected to be raised.
        
        Parameters:
        None
        
        Returns:
        None
        
        Functions Used:
        - `fits.Comp
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)), quantize_method=1)
        hdu._header['ZDITHER0'] = 'a'
        with pytest.raises(TypeError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZNAXIS', 'ZBITPIX'])
    def test_header_missing_keyword(self, kw):
        """
        Test that a KeyError is raised when a required keyword is missing from the header of a CompImageHDU.
        
        Parameters:
        -----------
        kw : str
        The keyword that should be present in the header.
        
        This function creates a `CompImageHDU` object with a 10x10 array of ones, deletes the specified keyword from its header, and then attempts to compress the HDU using the `compress_hdu` function. If the keyword is missing, a
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        del hdu._header[kw]
        with pytest.raises(KeyError) as exc:
            compress_hdu(hdu)
        assert kw in str(exc)

    @pytest.mark.parametrize('kw', ['ZNAXIS', 'ZVAL1', 'ZVAL2', 'ZBLANK', 'BLANK'])
    def test_header_value_int_overflow(self, kw):
        """
        Test that attempting to set an integer header keyword value to an overflow value raises an OverflowError.
        
        Args:
        kw (str): The keyword of the header to be set.
        
        Raises:
        OverflowError: If the header value overflows the maximum integer value.
        
        Functions Used:
        - `fits.CompImageHDU`: Creates a composite image HDU.
        - `MAX_INT`: The maximum integer value.
        - `compress_hdu`: Compresses the given HDU.
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = MAX_INT + 1
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZTILE1', 'ZNAXIS1'])
    def test_header_value_long_overflow(self, kw):
        """
        Test that attempting to set a header keyword value to an overflowed long integer raises an OverflowError.
        
        Args:
        kw (str): The header keyword to be set.
        
        Raises:
        OverflowError: If the header keyword value overflows the maximum allowed long integer value.
        
        Functions Used:
        - `fits.CompImageHDU`: Creates a composite image HDU.
        - `MAX_LONG`: Represents the maximum value for a long integer.
        - `compress_hdu`: Compress
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = MAX_LONG + 1
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['NAXIS1', 'NAXIS2', 'TNULL1', 'PCOUNT', 'THEAP'])
    def test_header_value_longlong_overflow(self, kw):
        """
        Test that attempting to set a header keyword value to an overflowed longlong value raises an OverflowError.
        
        Args:
        kw (str): The header keyword to be set.
        
        Raises:
        OverflowError: If the header keyword value overflows the longlong limit during compression.
        
        Functions Used:
        - `fits.CompImageHDU`: Creates a composite image HDU.
        - `MAX_LONGLONG`: Represents the maximum value for a C longlong type.
        - `compress_h
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = MAX_LONGLONG + 1
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZVAL3'])
    def test_header_value_float_overflow(self, kw):
        """
        Test that attempting to set a header keyword value to a floating-point number causing an overflow raises an OverflowError.
        
        Args:
        kw (str): The header keyword to be set to a large floating-point value.
        
        Raises:
        OverflowError: If the header keyword value exceeds the representable range of floating-point numbers.
        
        Functions Used:
        - `fits.CompImageHDU`: Creates a composite image HDU.
        - `compress_hdu`: Compresses the given HDU.
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = 1e300
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['NAXIS1', 'NAXIS2', 'TFIELDS', 'PCOUNT'])
    def test_header_value_negative(self, kw):
        """
        Test that a ValueError is raised when attempting to set a header keyword to a negative value.
        
        Args:
        kw (str): The header keyword to be set to a negative value.
        
        Raises:
        ValueError: If the header keyword is set to a negative value, a ValueError is raised.
        
        Notes:
        This function creates a `CompImageHDU` object with a single header keyword set to -1. It then attempts to compress the HDU using the `compress_hdu` function
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = -1
        with pytest.raises(ValueError) as exc:
            compress_hdu(hdu)
        assert '{} should not be negative.'.format(kw) in str(exc)

    @pytest.mark.parametrize(
        ('kw', 'limit'),
        [('ZNAXIS', 999),
         ('TFIELDS', 999)])
    def test_header_value_exceeds_custom_limit(self, kw, limit):
        """
        Test that attempting to set a header keyword value exceeding the custom limit raises a ValueError.
        
        Args:
        kw (str): The header keyword to be modified.
        limit (int): The custom limit for the header keyword value.
        
        Raises:
        ValueError: If the header keyword value exceeds the custom limit.
        
        Functions Used:
        - `fits.CompImageHDU`: Creates a composite image HDU.
        - `compress_hdu`: Compresses the HDU, which checks the header
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = limit + 1
        with pytest.raises(ValueError) as exc:
            compress_hdu(hdu)
        assert kw in str(exc)

    @pytest.mark.parametrize('kw', ['TTYPE1', 'TFORM1', 'ZCMPTYPE', 'ZNAME1',
                                    'ZQUANTIZ'])
    def test_header_value_no_string(self, kw):
        """
        Test that attempting to set a non-string value in the header of a FITS image HDU raises a TypeError when the `compress_hdu` function is called.
        
        Args:
        kw (str): The keyword to be used in setting the header value.
        
        Raises:
        TypeError: If a non-string value is assigned to the header keyword, this exception is raised when calling `compress_hdu`.
        
        Example:
        >>> hdu = fits.CompImageHDU(np.ones((10,
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = 1
        with pytest.raises(TypeError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['TZERO1', 'TSCAL1'])
    def test_header_value_no_double(self, kw):
        """
        Test that attempting to set a header keyword value to a non-string type raises a TypeError.
        
        This function creates a `CompImageHDU` object with a single header keyword set to '1'. It then attempts to compress the HDU using the `compress_hdu` function, which should raise a TypeError due to the non-string value.
        
        Parameters:
        - kw (str): The header keyword to be set.
        
        Raises:
        - TypeError: If the header keyword is set to a
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = '1'
        with pytest.raises(TypeError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZSCALE', 'ZZERO'])
    def test_header_value_no_double_int_image(self, kw):
        """
        Test that an error is raised when attempting to set a header keyword value to a string in a CompImageHDU.
        
        Args:
        kw (str): The header keyword to be set.
        
        Raises:
        TypeError: If the header keyword value is set to a string instead of an integer, an error is expected to be raised.
        
        Returns:
        None
        
        Functions Used:
        - `fits.CompImageHDU`: Creates a composite image HDU with a specified data array.
        """

        hdu = fits.CompImageHDU(np.ones((10, 10), dtype=np.int32))
        hdu._header[kw] = '1'
        with pytest.raises(TypeError):
            compress_hdu(hdu)
