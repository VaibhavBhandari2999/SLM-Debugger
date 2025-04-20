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
        setUpTestData(cls)
        This method is a class method used to set up test data for a test class. It creates a single instance of a user with the following parameters:
        - username (str): The username for the user, set to "inactive".
        - password (str): The password for the user, set to "password".
        - is_active (bool): A boolean indicating whether the user is active, set to False.
        
        Parameters:
        - cls: The test class itself, used to create
        """

        User.objects.create_user(
            username="inactive", password="password", is_active=False
        )

    def test_inactive_user(self):
        """
        Tests the behavior of the AdminAuthenticationForm with an inactive user.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - data (dict): A dictionary containing the username and password for the inactive user.
        
        Keywords:
        - form (AdminAuthenticationForm): The form instance to be tested.
        
        Details:
        This function tests the `AdminAuthenticationForm` to ensure that it correctly identifies an inactive user and returns an appropriate error message.
        The `data` dictionary contains the username and password
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
