from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import AdminForm
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings

from .admin import ArticleForm


# To verify that the login form rejects inactive users, use an authentication
# backend that allows them.
@override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.AllowAllUsersModelBackend'])
class AdminAuthenticationFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='inactive', password='password', is_active=False)

    def test_inactive_user(self):
        """
        Tests the behavior of the AdminAuthenticationForm with an inactive user.
        
        This function verifies that when an inactive user attempts to log in, the form returns a specific error message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - data (dict): A dictionary containing the login credentials for the inactive user. It includes:
        - 'username': The username of the inactive user.
        - 'password': The password for the inactive user.
        
        Keywords:
        - form (AdminAuthenticationForm
        """

        data = {
            'username': 'inactive',
            'password': 'password',
        }
        form = AdminAuthenticationForm(None, data)
        self.assertEqual(form.non_field_errors(), ['This account is inactive.'])


class AdminFormTests(SimpleTestCase):
    def test_repr(self):
        """
        Test the representation of an AdminForm object.
        
        This function checks the string representation of an AdminForm instance. The AdminForm is created with a specified form and fieldsets. The fieldsets are a tuple containing a dictionary with keys 'classes' and 'fields'. The function asserts that the representation of the AdminForm matches the expected string.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Elements:
        - form: The form associated with the AdminForm.
        - fieldsets: A tuple of
        """

        fieldsets = (
            ('My fields', {
                'classes': ['collapse'],
                'fields': ('url', 'title', 'content', 'sites'),
            }),
        )
        form = ArticleForm()
        admin_form = AdminForm(form, fieldsets, {})
        self.assertEqual(
            repr(admin_form),
            "<AdminForm: form=ArticleForm fieldsets=(('My fields', "
            "{'classes': ['collapse'], "
            "'fields': ('url', 'title', 'content', 'sites')}),)>",
        )
