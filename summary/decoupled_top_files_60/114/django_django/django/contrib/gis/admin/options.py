from django.contrib.admin import ModelAdmin
from django.contrib.gis.db import models
from django.contrib.gis.forms import OSMWidget


class GeoModelAdminMixin:
    gis_widget = OSMWidget
    gis_widget_kwargs = {}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Generates a form field for a database field, specifically handling geometry fields.
        
        This method is used to customize the form field for a database field, especially for geometry fields. If the field is a geometry field with a dimension less than 3 or if the GIS widget supports 3D rendering, it sets the widget to a GIS-specific widget with provided keyword arguments. Otherwise, it falls back to the default form field generation.
        
        Parameters:
        db_field (django.db.models.Field): The database field for
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
