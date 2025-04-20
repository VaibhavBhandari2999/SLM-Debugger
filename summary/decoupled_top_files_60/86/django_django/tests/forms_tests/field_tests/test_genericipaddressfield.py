from django.core.exceptions import ValidationError
from django.forms import GenericIPAddressField
from django.test import SimpleTestCase


class GenericIPAddressFieldTest(SimpleTestCase):

    def test_generic_ipaddress_invalid_arguments(self):
        """
        Test the GenericIPAddressField with invalid arguments.
        
        This function checks for invalid arguments in the GenericIPAddressField. It raises a ValueError for the following cases:
        - When the protocol argument is set to an invalid value ('hamster').
        - When the protocol is set to 'ipv4' and unpack_ipv4 is also set to True.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the protocol argument is set to an invalid value or if the protocol is set to 'ipv4
        """

        with self.assertRaises(ValueError):
            GenericIPAddressField(protocol='hamster')
        with self.assertRaises(ValueError):
            GenericIPAddressField(protocol='ipv4', unpack_ipv4=True)

    def test_generic_ipaddress_as_generic(self):
        # The edge cases of the IPv6 validation code are not deeply tested
        # here, they are covered in the tests for django.utils.ipv6
        f = GenericIPAddressField()
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(f.clean(' 127.0.0.1 '), '127.0.0.1')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 or IPv6 address.'"):
            f.clean('foo')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 or IPv6 address.'"):
            f.clean('127.0.0.')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 or IPv6 address.'"):
            f.clean('1.2.3.4.5')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 or IPv6 address.'"):
            f.clean('256.125.1.5')
        self.assertEqual(f.clean(' fe80::223:6cff:fe8a:2e8a '), 'fe80::223:6cff:fe8a:2e8a')
        self.assertEqual(f.clean(' 2a02::223:6cff:fe8a:2e8a '), '2a02::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('12345:2:3:4')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('1::2:3::4')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('foo::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('1::2:3:4:5:6:7:8')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('1:2')

    def test_generic_ipaddress_as_ipv4_only(self):
        """
        Tests the behavior of the GenericIPAddressField with the protocol set to 'IPv4'.
        
        This function validates the following:
        - The field requires a value and raises a ValidationError if an empty string or None is provided.
        - It correctly handles and validates a valid IPv4 address.
        - It raises a ValidationError for invalid IPv4 addresses, including addresses with incorrect formats, too many segments, or invalid segment values.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValidationError: If the input does not
        """

        f = GenericIPAddressField(protocol="IPv4")
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(f.clean(' 127.0.0.1 '), '127.0.0.1')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 address.'"):
            f.clean('foo')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 address.'"):
            f.clean('127.0.0.')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 address.'"):
            f.clean('1.2.3.4.5')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 address.'"):
            f.clean('256.125.1.5')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 address.'"):
            f.clean('fe80::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 address.'"):
            f.clean('2a02::223:6cff:fe8a:2e8a')

    def test_generic_ipaddress_as_ipv6_only(self):
        f = GenericIPAddressField(protocol="IPv6")
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv6 address.'"):
            f.clean('127.0.0.1')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv6 address.'"):
            f.clean('foo')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv6 address.'"):
            f.clean('127.0.0.')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv6 address.'"):
            f.clean('1.2.3.4.5')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv6 address.'"):
            f.clean('256.125.1.5')
        self.assertEqual(f.clean(' fe80::223:6cff:fe8a:2e8a '), 'fe80::223:6cff:fe8a:2e8a')
        self.assertEqual(f.clean(' 2a02::223:6cff:fe8a:2e8a '), '2a02::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('12345:2:3:4')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('1::2:3::4')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('foo::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('1::2:3:4:5:6:7:8')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('1:2')

    def test_generic_ipaddress_as_generic_not_required(self):
        f = GenericIPAddressField(required=False)
        self.assertEqual(f.clean(''), '')
        self.assertEqual(f.clean(None), '')
        self.assertEqual(f.clean('127.0.0.1'), '127.0.0.1')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 or IPv6 address.'"):
            f.clean('foo')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 or IPv6 address.'"):
            f.clean('127.0.0.')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 or IPv6 address.'"):
            f.clean('1.2.3.4.5')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid IPv4 or IPv6 address.'"):
            f.clean('256.125.1.5')
        self.assertEqual(f.clean(' fe80::223:6cff:fe8a:2e8a '), 'fe80::223:6cff:fe8a:2e8a')
        self.assertEqual(f.clean(' 2a02::223:6cff:fe8a:2e8a '), '2a02::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('12345:2:3:4')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('1::2:3::4')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('foo::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('1::2:3:4:5:6:7:8')
        with self.assertRaisesMessage(ValidationError, "'This is not a valid IPv6 address.'"):
            f.clean('1:2')

    def test_generic_ipaddress_normalization(self):
        """
        Test the normalization of IP addresses for a GenericIPAddressField.
        
        This function tests the normalization code for a GenericIPAddressField. It checks the following:
        - Normalizes IPv4 addresses with leading zeros and spaces.
        - Normalizes IPv6 addresses with leading zeros and spaces.
        - Ensures that the 'unpack_ipv4' parameter works correctly, converting IPv4-mapped IPv6 addresses to their IPv4 form.
        
        Parameters:
        - f (GenericIPAddressField): The field instance to test.
        
        Returns:
        - None
        """

        # Test the normalizing code
        f = GenericIPAddressField()
        self.assertEqual(f.clean(' ::ffff:0a0a:0a0a  '), '::ffff:10.10.10.10')
        self.assertEqual(f.clean(' ::ffff:10.10.10.10  '), '::ffff:10.10.10.10')
        self.assertEqual(f.clean(' 2001:000:a:0000:0:fe:fe:beef  '), '2001:0:a::fe:fe:beef')
        self.assertEqual(f.clean(' 2001::a:0000:0:fe:fe:beef  '), '2001:0:a::fe:fe:beef')

        f = GenericIPAddressField(unpack_ipv4=True)
        self.assertEqual(f.clean(' ::ffff:0a0a:0a0a'), '10.10.10.10')
