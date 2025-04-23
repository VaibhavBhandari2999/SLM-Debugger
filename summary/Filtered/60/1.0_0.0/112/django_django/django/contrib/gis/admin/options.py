from django.contrib.admin import ModelAdmin
from django.contrib.gis.db import models
from django.contrib.gis.forms import OSMWidget


class GeoModelAdminMixin:
    gis_widget = OSMWidget
    gis_widget_kwargs = {}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Generate a form field for a database field in a Django model.
        
        This method is used to customize the form field for a specific type of database field, particularly for geometry fields in GIS applications. It checks if the field is a `GeometryField` and if it supports 3D rendering or has a dimension less than 3. If these conditions are met, it sets a custom GIS widget for the form field. Otherwise, it falls back to the default form field handling.
        
        Parameters:
        db_field
        """

        if isinstance(db_field, models.GeometryField) and (
            db_field.dim < 3 or self.gis_widget.supports_3d
        ):
            kwargs["widget"] = self.gis_widget(**self.gis_widget_kwargs)
            return db_field.formfield(**kwargs)
        else:
            return super().formfield_for_dbfield(db_field, request, **kwargs)


class GISModelAdmin(GeoModelAdminMixin, ModelAdmin):
    pass
