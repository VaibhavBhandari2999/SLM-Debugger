"""
This Python file provides decorators for adding metadata to Django admin actions and displays. It includes three main decorators: `action`, `display`, and `register`. 

- **action**: This decorator allows you to easily add attributes like `allowed_permissions` and `short_description` to an admin action function. It simplifies the process of defining what permissions are required for an action and providing a user-friendly description.

- **display**: This decorator is used to add attributes such as `boolean`, `ordering`, `short_description`, and `empty_value_display` to a display function. These attributes help customize how data is displayed in the Django admin interface, including whether a field should be displayed as a boolean, how it should be ordered, and what value should
"""
def action(function=None, *, permissions=None, description=None):
    """
    Conveniently add attributes to an action function::

        @admin.action(
            permissions=['publish'],
            description='Mark selected stories as published',
        )
        def make_published(self, request, queryset):
            queryset.update(status='p')

    This is equivalent to setting some attributes (with the original, longer
    names) on the function directly::

        def make_published(self, request, queryset):
            queryset.update(status='p')
        make_published.allowed_permissions = ['publish']
        make_published.short_description = 'Mark selected stories as published'
    """
    def decorator(func):
        """
        Generate a Python docstring for the provided function.
        
        Args:
        func (function): The function to generate a docstring for.
        
        Returns:
        str: The generated docstring.
        """

        if permissions is not None:
            func.allowed_permissions = permissions
        if description is not None:
            func.short_description = description
        return func
    if function is None:
        return decorator
    else:
        return decorator(function)


def display(function=None, *, boolean=None, ordering=None, description=None, empty_value=None):
    """
    Conveniently add attributes to a display function::

        @admin.display(
            boolean=True,
            ordering='-publish_date',
            description='Is Published?',
        )
        def is_published(self, obj):
            return obj.publish_date is not None

    This is equivalent to setting some attributes (with the original, longer
    names) on the function directly::

        def is_published(self, obj):
            return obj.publish_date is not None
        is_published.boolean = True
        is_published.admin_order_field = '-publish_date'
        is_published.short_description = 'Is Published?'
    """
    def decorator(func):
        if boolean is not None and empty_value is not None:
            raise ValueError(
                'The boolean and empty_value arguments to the @display '
                'decorator are mutually exclusive.'
            )
        if boolean is not None:
            func.boolean = boolean
        if ordering is not None:
            func.admin_order_field = ordering
        if description is not None:
            func.short_description = description
        if empty_value is not None:
            func.empty_value_display = empty_value
        return func
    if function is None:
        return decorator
    else:
        return decorator(function)


def register(*models, site=None):
    """
    Register the given model(s) classes and wrapped ModelAdmin class with
    admin site:

    @register(Author)
    class AuthorAdmin(admin.ModelAdmin):
        pass

    The `site` kwarg is an admin site to use instead of the default admin site.
    """
    from django.contrib.admin import ModelAdmin
    from django.contrib.admin.sites import AdminSite, site as default_site

    def _model_admin_wrapper(admin_class):
        """
        Register one or more models with a custom ModelAdmin class.
        
        Args:
        admin_class (type): A subclass of ModelAdmin to use for the registered models.
        
        Raises:
        ValueError: If no models are provided, if the provided site is not an instance of AdminSite, or if the provided admin_class is not a subclass of ModelAdmin.
        
        Returns:
        type: The provided admin_class, which is now registered with the specified models on the given admin_site.
        """

        if not models:
            raise ValueError('At least one model must be passed to register.')

        admin_site = site or default_site

        if not isinstance(admin_site, AdminSite):
            raise ValueError('site must subclass AdminSite')

        if not issubclass(admin_class, ModelAdmin):
            raise ValueError('Wrapped class must subclass ModelAdmin.')

        admin_site.register(models, admin_class=admin_class)

        return admin_class
    return _model_admin_wrapper
