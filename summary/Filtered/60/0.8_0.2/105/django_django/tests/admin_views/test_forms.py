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
        setUpTestData is a class method used to set up test data for a Django test case. It creates a single instance of a user with the following parameters:
        - username: The username of the user, set to "inactive".
        - password: The password of the user, set to "password".
        - is_active: A boolean indicating whether the user is active, set to False.
        
        This method is typically used to create initial data that is shared across multiple test methods within a test class. The created
        """

        User.objects.create_user(
            username="inactive", password="password", is_active=False
        )

    def test_inactive_user(self):
        """
        Tests the behavior of the AdminAuthenticationForm when an inactive user attempts to log in.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the non-field errors do not match the expected error message.
        
        Key Parameters:
        data (dict): A dictionary containing the login credentials for an inactive user.
        
        Keywords:
        form (AdminAuthenticationForm): The form instance to test.
        
        Details:
        This function verifies that when an inactive user tries to log in, the form returns a specific
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
