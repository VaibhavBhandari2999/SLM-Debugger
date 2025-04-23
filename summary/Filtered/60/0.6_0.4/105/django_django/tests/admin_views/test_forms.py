from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import AdminForm
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings

from .admin import ArticleForm


# To verify that the login form rejects inactive users, use an authentication
# backend that allows them.
@override_settings(
    AUTHENTICATION_BACKENDS=["django.contrib.auth.backends.AllowAllUsersModelBackend"]
)
class AdminAuthenticationFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData is a class method used in Django testing to create test data that will be shared across multiple test methods. It creates an inactive user with a specific username and password.
        
        Parameters:
        - cls: The class object for which the test data is being set up.
        
        Returns:
        - None: This method does not return anything. It creates a test user in the database.
        
        Key Points:
        - The user created is inactive, meaning it cannot log in.
        - The username is "inactive".
        - The
        """

        User.objects.create_user(
            username="inactive", password="password", is_active=False
        )

    def test_inactive_user(self):
        """
        Test the behavior of the AdminAuthenticationForm with an inactive user.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - data (dict): A dictionary containing the username and password for the inactive user.
        
        Keywords:
        - None
        
        Description:
        This function tests the AdminAuthenticationForm with a user account that is marked as inactive. It provides a dictionary with the username and password of the inactive user. The function checks if the form returns a non-field error indicating that the account
        """

        data = {
            "username": "inactive",
            "password": "password",
        }
        form = AdminAuthenticationForm(None, data)
        self.assertEqual(form.non_field_errors(), ["This account is inactive."])


class AdminFormTests(SimpleTestCase):
    def test_repr(self):
        fieldsets = (
            (
                "My fields",
                {
                    "classes": ["collapse"],
                    "fields": ("url", "title", "content", "sites"),
                },
            ),
        )
        form = ArticleForm()
        admin_form = AdminForm(form, fieldsets, {})
        self.assertEqual(
            repr(admin_form),
            "<AdminForm: form=ArticleForm fieldsets=(('My fields', "
            "{'classes': ['collapse'], "
            "'fields': ('url', 'title', 'content', 'sites')}),)>",
        )
