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
        This function is a decorator that can be used to add metadata to a function. It accepts two optional parameters: 'permissions' and 'description'. The 'permissions' parameter should be a list of strings representing the permissions required to execute the decorated function. The 'description' parameter should be a string providing a brief description of the function's purpose. The decorator modifies the decorated function by adding these metadata attributes. The function being decorated should return the same type of value as it would without the decorator.
        
        :param
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


def display(
    function=None, *, boolean=None, ordering=None, description=None, empty_value=None
):
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
                "The boolean and empty_value arguments to the @display "
                "decorator are mutually exclusive."
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
    from django.contrib.admin.sites import AdminSite
    from django.contrib.admin.sites import site as default_site

    def _model_admin_wrapper(admin_class):
        """
        Register one or more models with the specified ModelAdmin class in the given AdminSite.
        
        Args:
        admin_class (type): A subclass of ModelAdmin to use for the registered models.
        models (tuple): A tuple of one or more model classes to be registered.
        site (AdminSite, optional): The AdminSite instance to register the models with. Defaults to the default site.
        
        Returns:
        type: The admin_class itself, as it is passed through unchanged.
        
        Raises:
        ValueError:
        """

        if not models:
            raise ValueError("At least one model must be passed to register.")

        admin_site = site or default_site

        if not isinstance(admin_site, AdminSite):
            raise ValueError("site must subclass AdminSite")

        if not issubclass(admin_class, ModelAdmin):
            raise ValueError("Wrapped class must subclass ModelAdmin.")

        admin_site.register(models, admin_class=admin_class)

        return admin_class

    return _model_admin_wrapper
