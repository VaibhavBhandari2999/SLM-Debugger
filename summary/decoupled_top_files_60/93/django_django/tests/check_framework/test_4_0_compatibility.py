from django.core.checks import Error
from django.core.checks.compatibility.django_4_0 import check_csrf_trusted_origins
from django.test import SimpleTestCase
from django.test.utils import override_settings


class CheckCSRFTrustedOrigins(SimpleTestCase):
    @override_settings(CSRF_TRUSTED_ORIGINS=["example.com"])
    def test_invalid_url(self):
        """
        Tests the behavior of the `check_csrf_trusted_origins` function when provided with a `None` value.
        
        Parameters:
        - None
        
        Returns:
        - A list of `Error` objects indicating that the values in the CSRF_TRUSTED_ORIGINS setting must start with a scheme (http:// or https://) as of Django 4.0. The specific error message is provided in the `id` attribute of the `Error` object.
        """

        self.assertEqual(
            check_csrf_trusted_origins(None),
            [
                Error(
                    "As of Django 4.0, the values in the CSRF_TRUSTED_ORIGINS "
                    "setting must start with a scheme (usually http:// or "
                    "https://) but found example.com. See the release notes for "
                    "details.",
                    id="4_0.E001",
                )
            ],
        )

    @override_settings(
        CSRF_TRUSTED_ORIGINS=["http://example.com", "https://example.com"],
    )
    def test_valid_urls(self):
        self.assertEqual(check_csrf_trusted_origins(None), [])
