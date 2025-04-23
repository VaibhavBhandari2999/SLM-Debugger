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
        - form (AdminAuthenticationForm): The form instance to be tested.
        
        Details:
        This function tests the AdminAuthenticationForm to ensure that it correctly identifies an inactive user and returns a specific error message.
        """

        data = {
            "username": "inactive",
            "password": "password",
        }
        form = AdminAuthenticationForm(None, data)
        self.assertEqual(form.non_field_errors(), ["This account is inactive."])


class AdminFormTests(SimpleTestCase):
    def test_repr(self):
        """
        Tests the `AdminForm` representation.
        
        This function checks the representation of an `AdminForm` instance. The `AdminForm` is initialized with a form of `ArticleForm` and a fieldset containing a title, classes, and fields. The expected representation is a string that includes the form type, fieldset details, and the number of fieldsets.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - `fieldsets`: A tuple containing a single fieldset with a
        """

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
