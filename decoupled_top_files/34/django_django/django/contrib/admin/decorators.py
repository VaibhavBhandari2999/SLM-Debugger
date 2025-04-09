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
