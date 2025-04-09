"""
This Python file contains unit tests for Django authentication decorators, specifically `login_required` and `permission_required`. 

#### Classes:
1. **LoginRequiredTestCase**: Tests the functionality of the `login_required` decorator. It includes methods to verify that the decorator works correctly with callable objects and normal views. It also tests scenarios where the user is redirected to the login page and then allowed to access the view after logging in.

2. **PermissionsRequiredDecoratorTest**: Tests the `permission_required` decorator. It includes methods to check if a view can be accessed successfully when the user has the required permissions, as well as scenarios where the user is denied access due to missing permissions. The test cases cover both individual and multiple permission requirements.

#### Functions:
-
"""
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
        """
        Sets up test data for the class.
        
        This method creates a user with the username 'joe' and password 'qwerty'. It then adds the user the following permissions:
        - 'add_customuser'
        - 'change_customuser'
        
        Args:
        cls (cls): The class object.
        
        Returns:
        None
        """

        cls.user = models.User.objects.create(username='joe', password='qwerty')
        # Add permissions auth.add_customuser and auth.change_customuser
        perms = models.Permission.objects.filter(codename__in=('add_customuser', 'change_customuser'))
        cls.user.user_permissions.add(*perms)

    def test_many_permissions_pass(self):
        """
        Tests if a view with multiple permission requirements is accessed successfully.
        
        This test checks whether a view that requires multiple permissions ('auth_tests.add_customuser' and 'auth_tests.change_customuser') can be accessed successfully by a user with those permissions.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `permission_required`: Decorator to require specific permissions for a view.
        - `self.factory.get()`: Creates a GET request for the specified URL.
        -
        """


        @permission_required(['auth_tests.add_customuser', 'auth_tests.change_customuser'])
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/rand')
        request.user = self.user
        resp = a_view(request)
        self.assertEqual(resp.status_code, 200)

    def test_many_permissions_in_set_pass(self):
        """
        Tests if a view passes when given multiple permissions in a set.
        
        This function checks whether a view that requires multiple permissions (specifically 'auth_tests.add_customuser' and 'auth_tests.change_customuser') returns a successful HTTP response (status code 200) when called with a request from a user who has those permissions.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `@permission_required`: Decorator to require specific permissions for a view
        """


        @permission_required({'auth_tests.add_customuser', 'auth_tests.change_customuser'})
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/rand')
        request.user = self.user
        resp = a_view(request)
        self.assertEqual(resp.status_code, 200)

    def test_single_permission_pass(self):
        """
        Tests if a view with a single 'add_customuser' permission requirement returns a 200 HTTP response.
        
        This test function creates a view that requires the 'add_customuser' permission from the 'auth_tests' app. It then creates a GET request with a user who has this permission and checks if the view returns an HTTP 200 response.
        
        :param self: The current test case instance.
        :return: None
        """


        @permission_required('auth_tests.add_customuser')
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/rand')
        request.user = self.user
        resp = a_view(request)
        self.assertEqual(resp.status_code, 200)

    def test_permissioned_denied_redirect(self):
        """
        Tests the behavior of a view when permission is denied. The view requires specific permissions ('auth_tests.add_customuser', 'auth_tests.change_customuser', 'nonexistent-permission') to be granted. If any of these permissions are missing, the user is redirected to a different page (HTTP status code 302).
        
        Args:
        self: The current test case instance.
        
        Returns:
        None
        
        Functions Used:
        - `permission_required`: Decorator that checks if the user
        """


        @permission_required(['auth_tests.add_customuser', 'auth_tests.change_customuser', 'nonexistent-permission'])
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/rand')
        request.user = self.user
        resp = a_view(request)
        self.assertEqual(resp.status_code, 302)

    def test_permissioned_denied_exception_raised(self):
        """
        Raise PermissionDenied exception if the user does not have the required permissions.
        
        This function tests whether a PermissionDenied exception is raised when a user lacks the necessary permissions to access a view. The `@permission_required` decorator is used to enforce permission checks on the `a_view` function, which returns an HTTP response. The test case sets up a GET request with a user who has certain permissions but also lacks one, and then asserts that a PermissionDenied exception is raised when the view is called.
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
