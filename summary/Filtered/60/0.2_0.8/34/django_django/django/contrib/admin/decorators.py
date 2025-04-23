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
        Wrapper function to register one or more models with a custom ModelAdmin class.
        
        This function is designed to be used as a decorator to simplify the registration of models with Django's admin site. It ensures that the provided ModelAdmin class is correctly registered with the specified models.
        
        Parameters:
        admin_class (type): A subclass of ModelAdmin to be used for model registration.
        
        Returns:
        type: The same ModelAdmin class that was passed in, after registration.
        
        Raises:
        ValueError: If no models are
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
