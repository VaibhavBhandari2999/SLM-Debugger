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
        Test function to validate handling of unknown compression types in FITS HDUs.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the compression type is unknown.
        
        Description:
        This function creates a FITS CompImageHDU with an unknown compression type ('fun') and attempts to compress it using the `compress_hdu` function. It asserts that a ValueError is raised with the appropriate message indicating that the compression type is unrecognized.
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
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        del hdu._header
        with pytest.raises(AttributeError) as exc:
            compress_hdu(hdu)
        assert '_header' in str(exc)

    def test_invalid_tform(self):
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
        """
        Test the behavior of the `compress_hdu` function when a header keyword value exceeds the maximum allowed length for a long integer.
        
        Parameters:
        kw (str): The FITS header keyword to be set to a value that exceeds the maximum allowed length for a long integer.
        
        Returns:
        None: This function does not return any value. It raises an `OverflowError` if the header keyword value is too long.
        
        Raises:
        OverflowError: If the value of the specified header keyword exceeds the
        """

        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = MAX_LONG + 1
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['NAXIS1', 'NAXIS2', 'TNULL1', 'PCOUNT', 'THEAP'])
    def test_header_value_longlong_overflow(self, kw):
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = MAX_LONGLONG + 1
        with pytest.raises(OverflowError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZVAL3'])
    def test_header_value_float_overflow(self, kw):
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
        hdu = fits.CompImageHDU(np.ones((10, 10)))
        hdu._header[kw] = '1'
        with pytest.raises(TypeError):
            compress_hdu(hdu)

    @pytest.mark.parametrize('kw', ['ZSCALE', 'ZZERO'])
    def test_header_value_no_double_int_image(self, kw):
        """
        Test the behavior of the `compress_hdu` function when a header keyword value is set to a string that cannot be converted to an integer.
        
        Parameters:
        kw (str): The header keyword to be set.
        
        Returns:
        None: This function is expected to raise a TypeError if the header value cannot be converted to an integer.
        
        Raises:
        TypeError: If the header value is a string that cannot be converted to an integer, indicating that the function is correctly enforcing type checking.
        """

        hdu = fits.CompImageHDU(np.ones((10, 10), dtype=np.int32))
        hdu._header[kw] = '1'
        with pytest.raises(TypeError):
            compress_hdu(hdu)
