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
        Registers one or more models with the specified ModelAdmin class in the Django admin site.
        
        Args:
        admin_class (type): A subclass of ModelAdmin to be used for the models.
        
        Returns:
        type: The same ModelAdmin class that was passed in.
        
        Raises:
        ValueError: If no models are passed, if the provided site is not an instance of AdminSite, or if the admin_class is not a subclass of ModelAdmin.
        
        Parameters:
        admin_class (type): The ModelAdmin subclass
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
