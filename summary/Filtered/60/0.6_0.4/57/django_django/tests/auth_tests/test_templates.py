from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import (
    PasswordChangeDoneView, PasswordChangeView, PasswordResetCompleteView,
    PasswordResetDoneView, PasswordResetView,
)
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode

from .client import PasswordResetConfirmClient


@override_settings(ROOT_URLCONF='auth_tests.urls')
class AuthTemplateTests(TestCase):
    request_factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for a Django test case.
        
        This method creates a test user and sets up a request object with the user as the authenticated user. It is intended to be used as a class method in Django test cases.
        
        Parameters:
        cls (object): The test class instance.
        
        Returns:
        None: This method does not return any value. It sets up class-level attributes for the test case.
        
        Key Attributes Set:
        - cls.user: The test user object.
        - cls.request:
        """

        user = User.objects.create_user('jsmith', 'jsmith@example.com', 'pass')
        user = authenticate(username=user.username, password='pass')
        request = cls.request_factory.get('/somepath/')
        request.user = user
        cls.user, cls.request = user, request

    def test_PasswordResetView(self):
        response = PasswordResetView.as_view(success_url='dummy/')(self.request)
        self.assertContains(response, '<title>Password reset | Django site admin</title>')
        self.assertContains(response, '<h1>Password reset</h1>')

    def test_PasswordResetDoneView(self):
        response = PasswordResetDoneView.as_view()(self.request)
        self.assertContains(response, '<title>Password reset sent | Django site admin</title>')
        self.assertContains(response, '<h1>Password reset sent</h1>')

    def test_PasswordResetConfirmView_invalid_token(self):
        # PasswordResetConfirmView invalid token
        client = PasswordResetConfirmClient()
        url = reverse('password_reset_confirm', kwargs={'uidb64': 'Bad', 'token': 'Bad-Token'})
        response = client.get(url)
        self.assertContains(response, '<title>Password reset unsuccessful | Django site admin</title>')
        self.assertContains(response, '<h1>Password reset unsuccessful</h1>')

    def test_PasswordResetConfirmView_valid_token(self):
        # PasswordResetConfirmView valid token
        client = PasswordResetConfirmClient()
        default_token_generator = PasswordResetTokenGenerator()
        token = default_token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(str(self.user.pk).encode())
        url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        response = client.get(url)
        self.assertContains(response, '<title>Enter new password | Django site admin</title>')
        self.assertContains(response, '<h1>Enter new password</h1>')
        # The username is added to the password reset confirmation form to help
        # browser's password managers.
        self.assertContains(
            response,
            '<input style="display: none;" autocomplete="username" value="jsmith">',
        )

    def test_PasswordResetCompleteView(self):
        response = PasswordResetCompleteView.as_view()(self.request)
        self.assertContains(response, '<title>Password reset complete | Django site admin</title>')
        self.assertContains(response, '<h1>Password reset complete</h1>')

    def test_PasswordResetChangeView(self):
        response = PasswordChangeView.as_view(success_url='dummy/')(self.request)
        self.assertContains(response, '<title>Password change | Django site admin</title>')
        self.assertContains(response, '<h1>Password change</h1>')

    def test_PasswordChangeDoneView(self):
        """
        Tests the PasswordChangeDoneView function.
        
        This function tests the PasswordChangeDoneView, which is likely a view in a Django application responsible for handling the successful completion of a password change. The function sends a request to this view and checks if the response contains the expected title and heading.
        
        Parameters:
        - request: The HTTP request object used to simulate a user request.
        
        Returns:
        - None: This function does not return any value. It asserts that the response from the view contains the expected HTML elements.
        """

        response = PasswordChangeDoneView.as_view()(self.request)
        self.assertContains(response, '<title>Password change successful | Django site admin</title>')
        self.assertContains(response, '<h1>Password change successful</h1>')
