from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.urls.resolvers import RegexPattern, RoutePattern, get_resolver
from django.utils.translation import gettext_lazy as _


class RegexPatternTests(SimpleTestCase):

    def test_str(self):
        self.assertEqual(str(RegexPattern(_('^translated/$'))), '^translated/$')


class RoutePatternTests(SimpleTestCase):

    def test_str(self):
        self.assertEqual(str(RoutePattern(_('translated/'))), 'translated/')


class ResolverCacheTests(SimpleTestCase):
    @override_settings(ROOT_URLCONF='urlpatterns.path_urls')
    def test_resolver_cache_default__root_urlconf(self):
        """
        Tests the resolver cache for a default URLconf.
        
        This function checks that the resolver for a default URLconf (when no argument is passed) and for the settings.ROOT_URLCONF is the same cached object. It also ensures that the resolver for a different URLconf (urlpatterns.path_dynamic_urls) is a different object.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - self.assertIs(get_resolver(), get_resolver('urlpatterns.path_urls')): The resolver for the default URLconf and the
        """

        # resolver for a default URLconf (passing no argument) and for the
        # settings.ROOT_URLCONF is the same cached object.
        self.assertIs(get_resolver(), get_resolver('urlpatterns.path_urls'))
        self.assertIsNot(get_resolver(), get_resolver('urlpatterns.path_dynamic_urls'))
