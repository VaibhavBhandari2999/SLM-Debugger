from functools import update_wrapper

from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse


class Action(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=70)

    def __str__(self):
        return self.name


class ActionAdmin(admin.ModelAdmin):
    """
    A ModelAdmin for the Action model that changes the URL of the add_view
    to '<app name>/<model name>/!add/'
    The Action model has a CharField PK.
    """

    list_display = ('name', 'description')

    def remove_url(self, name):
        """
        Remove all entries named 'name' from the ModelAdmin instance URL
        patterns list
        """
        return [url for url in super().get_urls() if url.name != name]

    def get_urls(self):
        """
        Generates a list of URL patterns for the admin site.
        
        This function modifies the URL configuration for the admin site by adding a custom 'add_view' URL pattern at the beginning of the list. It first removes any existing 'add' URL patterns and then appends the new one. The function uses Django's `re_path` to define the URL pattern and `admin_site.admin_view` to wrap the view for permission checks.
        
        Parameters:
        - self: The instance of the class containing the method.
        """

        # Add the URL of our custom 'add_view' view to the front of the URLs
        # list.  Remove the existing one(s) first
        from django.urls import re_path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        view_name = '%s_%s_add' % info

        return [
            re_path('^!add/$', wrap(self.add_view), name=view_name),
        ] + self.remove_url(view_name)


class Person(models.Model):
    name = models.CharField(max_length=20)


class PersonAdmin(admin.ModelAdmin):

    def response_post_save_add(self, request, obj):
        return HttpResponseRedirect(
            reverse('admin:admin_custom_urls_person_history', args=[obj.pk]))

    def response_post_save_change(self, request, obj):
        return HttpResponseRedirect(
            reverse('admin:admin_custom_urls_person_delete', args=[obj.pk]))


class Car(models.Model):
    name = models.CharField(max_length=20)


class CarAdmin(admin.ModelAdmin):

    def response_add(self, request, obj, post_url_continue=None):
        """
        Generate a response after adding an object in the Django admin interface.
        
        This method is overridden to customize the URL that the user is redirected to after adding an object. It uses the `reverse` function to generate the URL for the car history of the newly added object.
        
        Parameters:
        request (HttpRequest): The HTTP request object.
        obj (object): The object that was just added.
        post_url_continue (str, optional): The URL to redirect to after the operation. Defaults to the URL for
        """

        return super().response_add(
            request, obj,
            post_url_continue=reverse('admin:admin_custom_urls_car_history', args=[obj.pk]),
        )


site = admin.AdminSite(name='admin_custom_urls')
site.register(Action, ActionAdmin)
site.register(Person, PersonAdmin)
site.register(Car, CarAdmin)
