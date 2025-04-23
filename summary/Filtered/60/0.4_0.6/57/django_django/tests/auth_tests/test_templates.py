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
        
        This method creates a user and authenticates it. It then creates a request object with the authenticated user and stores both the user and the request in class variables for use in tests.
        
        Parameters:
        cls (TestClass): The test class in which this method is defined.
        
        Returns:
        None: This method does not return anything. It modifies the class variables of the test class.
        
        Key Parameters:
        - `cls.request_factory`: A Django RequestFactory
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
        """
        Tests the PasswordResetConfirmView with an invalid token.
        
        This function tests the behavior of the PasswordResetConfirmView when an invalid token is provided. It uses a custom client to make a GET request to the view with a specific URL containing a bad token. The function asserts that the response contains the expected title and error message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The response contains the title '<title>Password reset unsuccessful | Django site admin</title>'.
        - The response
        """

        # PasswordResetConfirmView invalid token
        client = PasswordResetConfirmClient()
        url = reverse('password_reset_confirm', kwargs={'uidb64': 'Bad', 'token': 'Bad-Token'})
        response = client.get(url)
        self.assertContains(response, '<title>Password reset unsuccessful | Django site admin</title>')
        self.assertContains(response, '<h1>Password reset unsuccessful</h1>')

    def test_PasswordResetConfirmView_valid_token(self):
        """
        Tests the PasswordResetConfirmView with a valid token.
        
        This function tests the PasswordResetConfirmView using a valid token. It creates a client, generates a token for a user, constructs the URL for the password reset confirmation view, and sends a GET request. The function asserts that the response contains specific HTML elements, indicating that the view is rendering the password reset form correctly.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Elements:
        - `client`: A client object used to simulate a web
        """

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
        response = PasswordChangeDoneView.as_view()(self.request)
        self.assertContains(response, '<title>Password change successful | Django site admin</title>')
        self.assertContains(response, '<h1>Password change successful</h1>')
