"""
This Python file contains definitions and imports related to Django's admin interface. It includes various decorators, filters, and classes used for customizing and extending the Django admin functionality. The primary responsibilities involve setting up model administration, defining filter options, and automating the registration of models with the admin site.

The key components defined in this file are:
- **Decorators**: `action`, `display`, `register` - These are used to customize admin actions and display fields.
- **Filters**: Various subclasses of `ListFilter` such as `AllValuesFieldListFilter`, `BooleanFieldListFilter`, etc. - These define different types of filters that can be applied to admin lists.
- **Admin Classes**: `ModelAdmin`, `StackedInline
"""
from django.contrib.admin.decorators import action, display, register
from django.contrib.admin.filters import (
    AllValuesFieldListFilter, BooleanFieldListFilter, ChoicesFieldListFilter,
    DateFieldListFilter, EmptyFieldListFilter, FieldListFilter, ListFilter,
    RelatedFieldListFilter, RelatedOnlyFieldListFilter, SimpleListFilter,
)
from django.contrib.admin.options import (
    HORIZONTAL, VERTICAL, ModelAdmin, StackedInline, TabularInline,
)
from django.contrib.admin.sites import AdminSite, site
from django.utils.module_loading import autodiscover_modules

__all__ = [
    "action", "display", "register", "ModelAdmin", "HORIZONTAL", "VERTICAL",
    "StackedInline", "TabularInline", "AdminSite", "site", "ListFilter",
    "SimpleListFilter", "FieldListFilter", "BooleanFieldListFilter",
    "RelatedFieldListFilter", "ChoicesFieldListFilter", "DateFieldListFilter",
    "AllValuesFieldListFilter", "EmptyFieldListFilter",
    "RelatedOnlyFieldListFilter", "autodiscover",
]


def autodiscover():
    autodiscover_modules('admin', register_to=site)
