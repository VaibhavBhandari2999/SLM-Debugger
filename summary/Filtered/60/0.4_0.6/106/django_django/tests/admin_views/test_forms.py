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
        -------------------
        A class method that sets up test data for the entire test class. It creates an inactive user with the following parameters:
        - username: "inactive"
        - password: "password"
        - is_active: False
        
        Parameters:
        - cls: The test class itself, used to create the test data.
        
        Returns:
        - None: This method does not return anything. It creates a user object and stores it in the database for use in tests.
        """

        User.objects.create_user(
            username="inactive", password="password", is_active=False
        )

    def test_inactive_user(self):
        """
        Tests the behavior of the AdminAuthenticationForm with an inactive user.
        
        Args:
        None
        
        Returns:
        None
        
        Key Parameters:
        - data (dict): A dictionary containing the username and password for the inactive user.
        
        Keywords:
        - form (AdminAuthenticationForm): The form instance to test.
        
        Details:
        This function tests the AdminAuthenticationForm to ensure that it correctly identifies an inactive user and returns the appropriate error message.
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
