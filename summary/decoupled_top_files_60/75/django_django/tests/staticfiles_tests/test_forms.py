from urllib.parse import urljoin

from django.contrib.staticfiles import storage
from django.forms import Media
from django.templatetags.static import static
from django.test import SimpleTestCase, override_settings


class StaticTestStorage(storage.StaticFilesStorage):
    def url(self, name):
        return urljoin('https://example.com/assets/', name)


@override_settings(
    STATIC_URL='http://media.example.com/static/',
    INSTALLED_APPS=('django.contrib.staticfiles',),
    STATICFILES_STORAGE='staticfiles_tests.test_forms.StaticTestStorage',
)
class StaticFilesFormsMediaTestCase(SimpleTestCase):
    def test_absolute_url(self):
        """
        Tests the absolute URL generation for a Media object.
        
        This function creates a Media object with specified CSS and JavaScript file paths. It then generates a string representation of the Media object, which includes the absolute URLs for the CSS and JavaScript files. The function asserts that the generated string matches the expected output.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Details:
        - The Media object is initialized with CSS and JavaScript file paths.
        - The CSS paths include both relative and absolute paths.
        -
        """

        m = Media(
            css={'all': ('path/to/css1', '/path/to/css2')},
            js=(
                '/path/to/js1',
                'http://media.other.com/path/to/js2',
                'https://secure.other.com/path/to/js3',
                static('relative/path/to/js4'),
            ),
        )
        self.assertEqual(
            str(m),
            """<link href="https://example.com/assets/path/to/css1" type="text/css" media="all" rel="stylesheet">
<link href="/path/to/css2" type="text/css" media="all" rel="stylesheet">
<script src="/path/to/js1"></script>
<script src="http://media.other.com/path/to/js2"></script>
<script src="https://secure.other.com/path/to/js3"></script>
<script src="https://example.com/assets/relative/path/to/js4"></script>"""
        )
