from itertools import chain

from django.apps import apps
from django.core.checks import Error


def check_generic_foreign_keys(app_configs=None, **kwargs):
    """
    Check for GenericForeignKey fields in Django models.
    
    This function is designed to validate GenericForeignKey fields in Django models.
    
    Parameters:
    app_configs (list, optional): A list of AppConfig instances. If provided, only models from these apps will be checked. If not provided, all models will be checked. Default is None.
    **kwargs: Additional keyword arguments are not used in this function.
    
    Returns:
    list: A list of validation errors found in the GenericForeignKey fields. Each error is a dictionary
    """

    from .fields import GenericForeignKey

    if app_configs is None:
        models = apps.get_models()
    else:
        models = chain.from_iterable(app_config.get_models() for app_config in app_configs)
    errors = []
    fields = (
        obj for model in models for obj in vars(model).values()
        if isinstance(obj, GenericForeignKey)
    )
    for field in fields:
        errors.extend(field.check())
    return errors


def check_model_name_lengths(app_configs=None, **kwargs):
    if app_configs is None:
        models = apps.get_models()
    else:
        models = chain.from_iterable(app_config.get_models() for app_config in app_configs)
    errors = []
    for model in models:
        if len(model._meta.model_name) > 100:
            errors.append(
                Error(
                    'Model names must be at most 100 characters (got %d).' % (
                        len(model._meta.model_name),
                    ),
                    obj=model,
                    id='contenttypes.E005',
                )
            )
    return errors
