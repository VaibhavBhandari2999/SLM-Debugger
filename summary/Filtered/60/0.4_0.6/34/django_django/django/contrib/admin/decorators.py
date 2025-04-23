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
        Register one or more models with a custom ModelAdmin class to an AdminSite.
        
        This function wraps a provided ModelAdmin class and registers one or more models with it in an AdminSite. It ensures that the provided class is a subclass of ModelAdmin and that at least one model is passed for registration.
        
        Parameters:
        admin_class (type): A subclass of ModelAdmin to wrap and use for registration.
        
        Returns:
        type: The provided admin_class, which is now registered with the models.
        
        Raises:
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
