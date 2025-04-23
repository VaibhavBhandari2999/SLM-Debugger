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
    from django.contrib.admin.sites import site as default_site, AdminSite

    def _model_admin_wrapper(admin_class):
        """
        Register one or more models with a custom ModelAdmin class to the Django admin site.
        
        This function takes a custom ModelAdmin class and one or more Django model classes, and registers them with the Django admin site. It ensures that the provided ModelAdmin class is a subclass of ModelAdmin and that the provided models are valid Django models. The function also validates that a valid AdminSite instance is provided.
        
        Parameters:
        admin_class (type): A subclass of ModelAdmin to be used for the admin interface.
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
