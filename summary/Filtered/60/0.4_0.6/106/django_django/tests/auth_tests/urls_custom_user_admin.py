from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.urls import path

site = admin.AdminSite(name="custom_user_admin")


class CustomUserAdmin(UserAdmin):
    def log_change(self, request, obj, message):
        """
        Logs a change for the given object. This function is intended to be overridden by subclasses.
        
        Parameters:
        request (HttpRequest): The HTTP request object containing user information.
        obj (Model): The Django model instance that has been changed.
        message (str): A message describing the change.
        
        This function temporarily sets the primary key of the request user to 1 to avoid an error when logging the change, as the LogEntry.user column expects an integer. After logging, it restores the original primary key
        """

        # LogEntry.user column doesn't get altered to expect a UUID, so set an
        # integer manually to avoid causing an error.
        original_pk = request.user.pk
        request.user.pk = 1
        super().log_change(request, obj, message)
        request.user.pk = original_pk


site.register(get_user_model(), CustomUserAdmin)

urlpatterns = [
    path("admin/", site.urls),
]
