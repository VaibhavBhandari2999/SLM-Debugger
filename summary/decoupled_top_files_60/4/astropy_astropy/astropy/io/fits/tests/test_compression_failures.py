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
        Test function to check handling of unknown compression types in FITS HDUs.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the compression type is unknown, indicating that the function correctly identifies and raises an error for unsupported compression types.
        
        This function creates a FITS ImageHDU with a specified unknown compression type and tests whether the `compress_hdu` function raises a ValueError when attempting to compress the HDU with this unknown type.
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header['ZCMPTYPE'] = 'fun'
        with pytest.raises(ValueError) as exc:
            compress_hdu(hdu)
        assert 'Unrecognized compression type: fun' in str(exc)

    def test_zbitpix_unknown(self):
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header['ZBITPIX'] = 13
        with pytest.raises(ValueError) as exc:
            compress_hdu(hdu)
        assert 'Invalid value for BITPIX: 13' in str(exc)

    def test_data_none(self):
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu.data = None
        with pytest.raises(TypeError) as exc:
            compress_hdu(hdu)
        assert 'CompImageHDU.data must be a numpy.ndarray' in str(exc)

    def test_missing_internal_header(self):
        """
        Test for missing internal header in a FITS image HDU.
        
        This function checks that an AttributeError is raised when the internal header
        of a FITS image HDU is deleted before attempting to compress the HDU.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        pytest.raises(AttributeError): If the internal header is missing, an
        AttributeError should be raised when attempting to compress the HDU.
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        del hdu._header
        with pytest.raises(AttributeError) as exc:
            compress_hdu(hdu)
        assert '_header' in str(exc)

    def test_invalid_tform(self):
        """
        Test the function `compress_hdu` with an invalid TFORM header keyword.
        
        Parameters:
        None
        
        This test function creates a `CompImageHDU` object with a 10x10 array of ones. It then sets the 'TFORM1' header keyword to 'TX', which is an invalid format. The function `compress_hdu` is called with this HDU. The test expects a `RuntimeError` to be raised, and checks that the error message contains the
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header['TFORM1'] = 'TX'
        with pytest.raises(RuntimeError) as exc:
            compress_hdu(hdu)
        assert 'TX' in str(exc) and 'TFORM' in str(exc)

    def test_invalid_zdither(self):
        hdu = fits.CompImageHDU(np.ones((10, 10)), quantize_method=1)
        hdu._header['ZDITHER0'] = 'a'
        with pytest.raises(TypeError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZNAXIS', 'ZBITPIX'])
    def test_header_missing_keyword(self, kw):
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        del hdu._header[kw]
        with pytest.raises(KeyError) as exc:
            compress_hdu(hdu)
        assert kw in str(exc)

    @pytest.mark.parametrize('kw', ['ZNAXIS', 'ZVAL1', 'ZVAL2', 'ZBLANK', 'BLANK'])
    def test_header_value_int_overflow(self, kw):
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = MAX_INT + 1
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZTILE1', 'ZNAXIS1'])
    def test_header_value_long_overflow(self, kw):
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = MAX_LONG + 1
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['NAXIS1', 'NAXIS2', 'TNULL1', 'PCOUNT', 'THEAP'])
    def test_header_value_longlong_overflow(self, kw):
        """
        Test function to check for longlong overflow in header values.
        
        This function creates a FITS image HDU with a header containing a specified key and a value that exceeds the maximum limit for a longlong integer. It then attempts to compress the HDU and expects an OverflowError to be raised.
        
        Parameters:
        kw (str): The keyword in the header to which the longlong overflow value will be assigned.
        
        Returns:
        None: The function raises an OverflowError if the header value is within the
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = MAX_LONGLONG + 1
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZVAL3'])
    def test_header_value_float_overflow(self, kw):
        """
        Test function to check for float overflow in header values during compression.
        
        Parameters:
        kw (str): The keyword of the header to be set to a large float value (1e300).
        
        This function creates a FITS image HDU with a single image array and sets the specified header keyword to a very large float value (1e300). It then attempts to compress the HDU and expects an OverflowError to be raised due to the float overflow.
        
        Returns:
        None:
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = 1e300
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['NAXIS1', 'NAXIS2', 'TFIELDS', 'PCOUNT'])
    def test_header_value_negative(self, kw):
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
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = limit + 1
        with pytest.raises(ValueError) as exc:
            compress_hdu(hdu)
        assert kw in str(exc)

    @pytest.mark.parametrize('kw', ['TTYPE1', 'TFORM1', 'ZCMPTYPE', 'ZNAME1',
                                    'ZQUANTIZ'])
    def test_header_value_no_string(self, kw):
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = 1
        with pytest.raises(TypeError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['TZERO1', 'TSCAL1'])
    def test_header_value_no_double(self, kw):
        """
        Test that an error is raised when a header keyword value is set to a string with a double quote.
        
        Parameters:
        kw (str): The header keyword to be set.
        
        Returns:
        None: This function does not return a value. It raises a TypeError if the header keyword value is set to a string with a double quote.
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = '1'
        with pytest.raises(TypeError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZSCALE', 'ZZERO'])
    def test_header_value_no_double_int_image(self, kw):
        hdu = fits.CompImageHDU(np.ones((10, 10), dtype=np.int32))
        hdu._header[kw] = '1'
        with pytest.raises(TypeError):
            compress_hdu(hdu)
