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
        setUpTestData is a class method used in Django testing to create test data that will be shared across multiple test methods. It is a static method that does not take any parameters and does not return any value. The method creates an inactive user with the username "inactive" and the password "password". The is_active parameter is set to False, indicating that the user is not active.
        
        Key Parameters:
        - None
        
        Key Keyword Arguments:
        - None
        
        Input:
        - None
        
        Output:
        - None
        """

        User.objects.create_user(
            username="inactive", password="password", is_active=False
        )

    def test_inactive_user(self):
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
        
        This function checks the string representation of an `AdminForm` object. The `AdminForm` is created with a specific set of fieldsets, and the test asserts that the `repr` of the `AdminForm` matches the expected string. The key parameters are:
        - `fieldsets`: A tuple containing a single fieldset with a title, classes, and fields.
        - `form`: An instance of `ArticleForm`.
        
        The function does not return any
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
