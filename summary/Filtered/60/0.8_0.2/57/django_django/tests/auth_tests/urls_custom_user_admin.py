from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.urls import path

site = admin.AdminSite(name='custom_user_admin')


class CustomUserAdmin(UserAdmin):
    def log_change(self, request, object, message):
        """
        Logs a change for the given object with the specified message. This function temporarily sets the user's primary key to 1 to avoid issues with the LogEntry.user column, which does not expect a UUID. After logging the change, the original primary key is restored.
        
        :param request: The HTTP request object containing the user information.
        :type request: HttpRequest
        :param object: The object for which the change is being logged.
        :type object: Model instance
        :param message: The log message describing the change.
        :type
        """

        # LogEntry.user column doesn't get altered to expect a UUID, so set an
        # integer manually to avoid causing an error.
        original_pk = request.user.pk
        request.user.pk = 1
        super().log_change(request, object, message)
        request.user.pk = original_pk


site.register(get_user_model(), CustomUserAdmin)

urlpatterns = [
    path('admin/', site.urls),
]
