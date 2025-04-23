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
        This function returns a list of URL patterns for the admin site. It first removes any existing URL patterns for the 'add' view of the specified model and then adds a new custom URL pattern for the 'add' view. The function takes no parameters and returns a list of URL patterns.
        
        Key Details:
        - The function modifies the URL patterns for the specified model's 'add' view.
        - It uses Django's `re_path` to define the URL pattern.
        - The custom URL pattern is added
        """

        # Add the URL of our custom 'add_view' view to the front of the URLs
        # list.  Remove the existing one(s) first
        from django.urls import re_path

        def wrap(view):
            """
            This function wraps a view function to be used with the Django admin site. It takes a view function as an argument and returns a wrapped version of it. The wrapped function is decorated with `admin_site.admin_view`, which provides additional functionality for admin views. The wrapper function is created by updating the wrapped view's metadata using `update_wrapper`.
            
            Parameters:
            - view: A Django view function to be wrapped.
            
            Returns:
            - A wrapped version of the view function that can be used as an admin view.
            """

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
        return super().response_add(
            request, obj,
            post_url_continue=reverse('admin:admin_custom_urls_car_history', args=[obj.pk]),
        )


site = admin.AdminSite(name='admin_custom_urls')
site.register(Action, ActionAdmin)
site.register(Person, PersonAdmin)
site.register(Car, CarAdmin)
