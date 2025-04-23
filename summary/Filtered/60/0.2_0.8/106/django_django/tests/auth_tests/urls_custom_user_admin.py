from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.urls import path

site = admin.AdminSite(name="custom_user_admin")


class CustomUserAdmin(UserAdmin):
    def log_change(self, request, obj, message):
        """
        Logs a change for the given object.
        
        This function logs a change for the specified object using the provided request and message. It temporarily sets the user's primary key to 1 to avoid issues with the LogEntry.user column, which does not expect a UUID. After logging the change, it restores the original primary key.
        
        :param request: The request object containing user information.
        :param obj: The object for which the change is being logged.
        :param message: The log message describing the change.
        :returns:
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
