"""
The provided Python file contains unit tests for the `URLField` class from Django's forms framework. The tests cover various aspects of the `URLField`, including its widget rendering, validation rules, and behavior under different conditions. The `URLFieldTest` class inherits from `FormFieldAssertionsMixin` and `SimpleTestCase` and defines several test methods to ensure the `URLField` behaves as expected.

#### Main Classes and Functions:
- **URLFieldTest**: A test class that inherits from `FormFieldAssertionsMixin` and `SimpleTestCase`. It contains multiple test methods to validate the `URLField`.
- **test_urlfield_widget**: Tests the rendering of the `URLField` widget.
- **test_urlfield_widget_max_min_length**: Tests the
"""
from django.core.exceptions import ValidationError
from django.forms import URLField
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class URLFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_urlfield_widget(self):
        f = URLField()
        self.assertWidgetRendersTo(f, '<input type="url" name="f" id="id_f" required>')

    def test_urlfield_widget_max_min_length(self):
        """
        Tests the URLField widget's handling of min_length and max_length constraints.
        
        - Validates that a URL with the correct length is accepted.
        - Checks that the widget renders with the specified maxlength and minlength attributes.
        - Ensures that URLs shorter than the minimum length raise a ValidationError.
        - Ensures that URLs longer than the maximum length raise a ValidationError.
        """

        f = URLField(min_length=15, max_length=20)
        self.assertEqual('http://example.com', f.clean('http://example.com'))
        self.assertWidgetRendersTo(
            f,
            '<input id="id_f" type="url" name="f" maxlength="20" '
            'minlength="15" required>',
        )
        msg = "'Ensure this value has at least 15 characters (it has 12).'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('http://f.com')
        msg = "'Ensure this value has at most 20 characters (it has 37).'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('http://abcdefghijklmnopqrstuvwxyz.com')

    def test_urlfield_clean(self):
        """
        Tests the `clean` method of the `URLField` class.
        
        This method validates and normalizes URLs. It accepts a string representing
        a URL and returns a properly formatted URL. The function handles various
        types of URLs including those with query parameters, subdomains, IP addresses,
        and internationalized domain names (IDNs). It also ensures that the URL is
        correctly normalized by removing any trailing spaces.
        
        Args:
        url (str): The URL to be validated
        """

        f = URLField(required=False)
        tests = [
            ('http://localhost', 'http://localhost'),
            ('http://example.com', 'http://example.com'),
            ('http://example.com/test', 'http://example.com/test'),
            ('http://example.com.', 'http://example.com.'),
            ('http://www.example.com', 'http://www.example.com'),
            ('http://www.example.com:8000/test', 'http://www.example.com:8000/test'),
            (
                'http://example.com?some_param=some_value',
                'http://example.com?some_param=some_value',
            ),
            ('valid-with-hyphens.com', 'http://valid-with-hyphens.com'),
            ('subdomain.domain.com', 'http://subdomain.domain.com'),
            ('http://200.8.9.10', 'http://200.8.9.10'),
            ('http://200.8.9.10:8000/test', 'http://200.8.9.10:8000/test'),
            ('http://valid-----hyphens.com', 'http://valid-----hyphens.com'),
            (
                'http://some.idn.xyzäöüßabc.domain.com:123/blah',
                'http://some.idn.xyz\xe4\xf6\xfc\xdfabc.domain.com:123/blah',
            ),
            (
                'www.example.com/s/http://code.djangoproject.com/ticket/13804',
                'http://www.example.com/s/http://code.djangoproject.com/ticket/13804',
            ),
            # Normalization.
            ('http://example.com/     ', 'http://example.com/'),
            # Valid IDN.
            ('http://עברית.idn.icann.org/', 'http://עברית.idn.icann.org/'),
            ('http://sãopaulo.com/', 'http://sãopaulo.com/'),
            ('http://sãopaulo.com.br/', 'http://sãopaulo.com.br/'),
            ('http://пример.испытание/', 'http://пример.испытание/'),
            ('http://مثال.إختبار/', 'http://مثال.إختبار/'),
            ('http://例子.测试/', 'http://例子.测试/'),
            ('http://例子.測試/', 'http://例子.測試/'),
            ('http://उदाहरण.परीक्षा/', 'http://उदाहरण.परीक्षा/',),
            ('http://例え.テスト/', 'http://例え.テスト/'),
            ('http://مثال.آزمایشی/', 'http://مثال.آزمایشی/'),
            ('http://실례.테스트/', 'http://실례.테스트/'),
            ('http://العربية.idn.icann.org/', 'http://العربية.idn.icann.org/'),
            # IPv6.
            ('http://[12:34::3a53]/', 'http://[12:34::3a53]/'),
            ('http://[a34:9238::]:8080/', 'http://[a34:9238::]:8080/'),
        ]
        for url, expected in tests:
            with self.subTest(url=url):
                self.assertEqual(f.clean(url), expected)

    def test_urlfield_clean_invalid(self):
        """
        Tests the validation of invalid URLs using the URLField clean method. The function iterates through a list of test cases, each representing an invalid URL, and validates them using the URLField clean method. It raises a ValidationError with the message 'Enter a valid URL.' for each invalid URL.
        """

        f = URLField()
        tests = [
            'foo',
            'com.',
            '.',
            'http://',
            'http://example',
            'http://example.',
            'http://.com',
            'http://invalid-.com',
            'http://-invalid.com',
            'http://inv-.alid-.com',
            'http://inv-.-alid.com',
            '[a',
            'http://[a',
            # Non-string.
            23,
            # Hangs "forever" before fixing a catastrophic backtracking,
            # see #11198.
            'http://%s' % ('X' * 60,),
            # A second example, to make sure the problem is really addressed,
            # even on domains that don't fail the domain label length check in
            # the regex.
            'http://%s' % ("X" * 200,),
        ]
        msg = "'Enter a valid URL.'"
        for value in tests:
            with self.subTest(value=value):
                with self.assertRaisesMessage(ValidationError, msg):
                    f.clean(value)

    def test_urlfield_clean_required(self):
        """
        Tests the validation of an empty or null value for a URLField.
        
        This function checks if the `clean` method of a URLField raises a ValidationError
        with the message "'This field is required.'" when passed None or an empty string.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the URLField does not raise the expected error message.
        
        Important Functions:
        - URLField: The field being tested.
        - clean: The method
        """

        f = URLField()
        msg = "'This field is required.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(None)
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('')

    def test_urlfield_clean_not_required(self):
        """
        Tests the clean method of the URLField when required is set to False. The function creates an instance of URLField with required set to False, then calls the clean method with None and an empty string as inputs. It asserts that the clean method returns an empty string for both inputs.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - URLField: Creates an instance of the URLField with required set to False.
        - clean: Cleans and validates the input
        """

        f = URLField(required=False)
        self.assertEqual(f.clean(None), '')
        self.assertEqual(f.clean(''), '')

    def test_urlfield_strip_on_none_value(self):
        """
        Tests the behavior of the URLField when cleaning an empty string or None value. The URLField is configured with required=False and empty_value=None. Cleaning an empty string or None returns None.
        
        Args:
        self: The instance of the test case class.
        
        Returns:
        None: The function asserts the expected behavior without returning any value.
        
        Functions Used:
        - URLField: Configures the field with specified parameters.
        - clean: Cleans and validates the input value.
        - assert
        """

        f = URLField(required=False, empty_value=None)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))

    def test_urlfield_unable_to_set_strip_kwarg(self):
        """
        Raises a TypeError when attempting to set the `strip` keyword argument in the initialization of a URLField.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If `URLField()` is called with multiple values for the `strip` keyword argument.
        
        Important Functions:
        - `URLField()`: The URLField class constructor.
        - `self.assertRaisesMessage()`: Used to assert that a specific exception is raised with a given message.
        """

        msg = "__init__() got multiple values for keyword argument 'strip'"
        with self.assertRaisesMessage(TypeError, msg):
            URLField(strip=False)
