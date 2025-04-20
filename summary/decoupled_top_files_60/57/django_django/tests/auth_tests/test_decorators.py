from django.conf import settings
from django.contrib.auth import models
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from .test_views import AuthViewsTestCase


@override_settings(ROOT_URLCONF='auth_tests.urls')
class LoginRequiredTestCase(AuthViewsTestCase):
    """
    Tests the login_required decorators
    """

    def test_callable(self):
        """
        login_required is assignable to callable objects.
        """
        class CallableView:
            def __call__(self, *args, **kwargs):
                pass
        login_required(CallableView())

    def test_view(self):
        """
        login_required is assignable to normal views.
        """
        def normal_view(request):
            pass
        login_required(normal_view)

    def test_login_required(self, view_url='/login_required/', login_url=None):
        """
        login_required works on a simple view wrapped in a login_required
        decorator.
        """
        if login_url is None:
            login_url = settings.LOGIN_URL
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(login_url, response.url)
        self.login()
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)

    def test_login_required_next_url(self):
        """
        login_required works on a simple view wrapped in a login_required
        decorator with a login_url set.
        """
        self.test_login_required(view_url='/login_required_login_url/', login_url='/somewhere/')


class PermissionsRequiredDecoratorTest(TestCase):
    """
    Tests for the permission_required decorator
    """
    factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        cls.user = models.User.objects.create(username='joe', password='qwerty')
        # Add permissions auth.add_customuser and auth.change_customuser
        perms = models.Permission.objects.filter(codename__in=('add_customuser', 'change_customuser'))
        cls.user.user_permissions.add(*perms)

    def test_many_permissions_pass(self):
        """
        Tests the view function 'a_view' with multiple permission requirements.
        
        This function checks if a user with the required permissions can access the view function 'a_view'. The view function requires the user to have either 'auth_tests.add_customuser' or 'auth_tests.change_customuser' permissions. The test creates a mock request with a user that has these permissions and calls the view function. If the user has the required permissions, the view function should return a 200 HTTP response.
        
        Parameters:
        """


        @permission_required(['auth_tests.add_customuser', 'auth_tests.change_customuser'])
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/rand')
        request.user = self.user
        resp = a_view(request)
        self.assertEqual(resp.status_code, 200)

    def test_many_permissions_in_set_pass(self):

        @permission_required({'auth_tests.add_customuser', 'auth_tests.change_customuser'})
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/rand')
        request.user = self.user
        resp = a_view(request)
        self.assertEqual(resp.status_code, 200)

    def test_single_permission_pass(self):
        """
        Tests the behavior of a view function that requires a single permission.
        
        This function checks if a view function, which requires the 'auth_tests.add_customuser' permission, can be accessed successfully by a user who has this permission.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A view function `a_view` is defined, which requires the 'auth_tests.add_customuser' permission.
        - A GET request is created using `self.factory.get('/rand')`.
        - The user associated
        """


        @permission_required('auth_tests.add_customuser')
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/rand')
        request.user = self.user
        resp = a_view(request)
        self.assertEqual(resp.status_code, 200)

    def test_permissioned_denied_redirect(self):

        @permission_required(['auth_tests.add_customuser', 'auth_tests.change_customuser', 'nonexistent-permission'])
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/rand')
        request.user = self.user
        resp = a_view(request)
        self.assertEqual(resp.status_code, 302)

    def test_permissioned_denied_exception_raised(self):
        """
        Tests that a PermissionDenied exception is raised when the user does not have the required permissions.
        
        This function tests a view that requires specific permissions. If the user lacks any of the required permissions, a PermissionDenied exception is raised.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        PermissionDenied: If the user does not have the required permissions.
        
        Usage:
        This function is typically used in test cases to ensure that a view enforces the correct permission requirements.
        """


        @permission_required([
            'auth_tests.add_customuser', 'auth_tests.change_customuser', 'nonexistent-permission'
        ], raise_exception=True)
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/rand')
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            a_view(request)
